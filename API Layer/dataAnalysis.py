import numpy as np
from scipy.signal import butter, filtfilt
from scipy.integrate import cumulative_trapezoid
import matplotlib.pyplot as plt

fs = 840.0  # Sampling rate in Hz
g = 9.80665 # Graviational constant

# Masses in kg
m_body = 92
m_bar = 90

'''
Info to record:

Consentric mean force (N)
Consentric mean power (W)
Consentric mean force / BM (W/kg)
Consentric peak velocity (m/s)
Consentric RFD (N/s)
Consentric RFD / BM (N/s/kg)
Consentric time to peak force (ms)
Contraction time (ms)

Esentric stuff?

Flight time (ms)
Jump height (cm)

Peak net takeoff force (N)
Peak net takeoff force / BM (N/kg)
Vertical veloctity at takeoff (m/s)

'''

# Apply Butterworth lowpass filter
def lowpass(x, fs, fc=30.0, order=4):
    nyq = fs / 2.0
    Wn = fc / nyq
    if not (0 < Wn < 1):
        raise ValueError(f"Cutoff {fc} Hz invalid for fs={fs} Hz (Wn={Wn})")
    b, a = butter(order, Wn, btype='low')
    return filtfilt(b, a, x)

def detectTakeoff(a_inertial):
    baseline = np.mean(a_inertial[:int(0.2*fs)])  # First 0.2 s as baseline

    jump_start_threshold = 2.0  # m/s² change from baseline
    start_candidates = np.where((a_inertial - baseline) > jump_start_threshold)[0]

    if len(start_candidates) == 0:
        return None, None

    start_idx = start_candidates[0]
    # Wherever the threashold was activated, backtrack to beginning of jump
    while start_idx > 0 and a_inertial[start_idx] > 0.5:
        start_idx -= 1

    # Find next place a_inertial crosses 0 acceleration to find takeoff
    takeoff_idx = np.argmax(a_inertial[start_idx:] < 0) + start_idx

    return start_idx, takeoff_idx

def calibrate_if_stationary(a_inertial, sampling_rate):
    n_samples = int(0.25 * sampling_rate)
    if np.all((a_inertial[:n_samples]-a_inertial[0] >= -0.3) & (a_inertial[:n_samples]-a_inertial[0] <= 0.3)):
        calibration_value = np.mean(a_inertial[:n_samples], axis=0)
        print(f"calibration: {calibration_value}")
        return calibration_value
    else:
        print(f"no calibration_value")
        return 0  # Not stationary, no calibration

def analyseDataframe(df):
    a_measured = np.array(df["az"])
    t = np.array(df["time"])/1000
    t = t - t[0] # Ensure timings start from 0

    m_system = m_body + m_bar

    print(df.head())
    print(df.info())

    # Remove gravity from acceleration
    a_inertial = lowpass(a_measured, fs, fc=25.0) - g

    # If not moving then calibrate acceleration to 0 (crude and can be improved later)
    calibrate = calibrate_if_stationary(a_inertial, 800)
    a_inertial = np.array(a_inertial) - calibrate

    # Find index of data where acceleration starts and stops
    start_idx, takeoff_idx = detectTakeoff(a_inertial)
    if ((start_idx == None) or (takeoff_idx == None) or (takeoff_idx == start_idx) or (start_idx > takeoff_idx)):
        return {
            "acceleration": list(a_inertial)[0::10],
            "time": list(t)[0::10]
        }

    # Get the peak acceleration index
    a_peak_net_idx = np.argmax(a_inertial[start_idx:takeoff_idx]) + start_idx
    peak_net_acceleration = a_inertial[a_peak_net_idx]

    # Time to peak force (assuming peak force = peak accel)
    time_to_peak_force = t[a_peak_net_idx] - t[start_idx]

    # Get average net force
    a_average_net = np.average(a_inertial[start_idx:takeoff_idx])

    v = np.zeros_like(a_inertial)
    v[start_idx:] = cumulative_trapezoid(
        a_inertial[start_idx:], 
        t[start_idx:], 
        initial=0
    )
    plt.plot(t, v, label='V (m/s)', linewidth=2)

    # Find velocity at takeoff
    takeoff_velocity = v[takeoff_idx]

    impulse = m_system * takeoff_velocity
    jump_height = (takeoff_velocity**2 / (2*g)) * 100 #cm
    flight_time = 2 * takeoff_velocity / g * 1000

    # Force and RFD
    forces =  m_system * a_inertial
    peak_force = np.max(forces[start_idx:takeoff_idx])
    peak_force_per_BM = peak_force / m_body

    mean_force = m_system * np.mean(a_inertial[start_idx:takeoff_idx])
    mean_force_per_BM = mean_force / m_body

    # Measure first 200 ms of avg RFD
    window_end_time = t[start_idx] + 0.2 
    end_idx = np.argmin(np.abs(t - window_end_time))
    avg_RFD_0_200 = (forces[end_idx] - forces[start_idx]) / (t[end_idx] - t[start_idx])
    avg_RFD_0_200_per_BM = avg_RFD_0_200 / m_body

    # Power
    GRF = a_inertial * m_system
    power = GRF * v
    plt.plot(t[start_idx:takeoff_idx], power[start_idx:takeoff_idx]/1000, label='Pwr (Kw)', linewidth=2)

    peak_power = np.max(power)
    work_done = np.trapezoid(power[start_idx:takeoff_idx], t[start_idx:takeoff_idx])

    time_window = t[takeoff_idx] - t[start_idx]
    avg_power = np.trapezoid(power[start_idx:takeoff_idx], t[start_idx:takeoff_idx]) / time_window

    # plt.axvline(t[start_idx], color='red', linestyle=':', label='Push End')
    # plt.axvline(t[takeoff_idx], color='red', linestyle=':', label='Push Start')
    # plt.axvline(t[a_peak_net_idx], color='green', linestyle='--', label='Peak force')

    # plt.axhline(a_inertial[a_peak_net_idx], color='blue', linestyle='--', label='Landing')

    # plt.plot(t, a_inertial, label='Raw Acceleration', marker='.', alpha=0.5)
    # plt.ylabel('Acceleration (m/s²)')
    # plt.xlabel('Time (s)')
    # plt.title('Jump Detection: Filtered Acceleration with Takeoff and Landing')
    # plt.legend()
    # plt.ylim((-15,15))
    # plt.grid(True)
    # plt.savefig("test")

    return {
        # --- Concentric phase metrics ---
        "concentric_mean_force_N": round(mean_force, 2),
        "concentric_peak_force_N": round(peak_force, 2),

        "concentric_mean_power_W": round(avg_power, 2),
        "concentric_peak_power_W": round(peak_power, 2),
        
        "concentric_mean_force_per_BM_W_per_kg": round(mean_force_per_BM, 2),
        "concentric_peak_velocity_m_per_s": round(takeoff_velocity, 2),
        "concentric_RFD_N_per_s": round(avg_RFD_0_200, 2),
        "concentric_RFD_per_BM_N_per_s_per_kg": round(avg_RFD_0_200_per_BM, 2),
        "concentric_time_to_peak_force_ms": round(time_to_peak_force * 1000, 2),
        "contraction_time_ms": round((t[takeoff_idx] - t[start_idx]) * 1000, 2),

        # --- Flight / outcome metrics ---
        "flight_time_ms": round(flight_time, 2),
        "jump_height_cm": round(jump_height, 2),

        # --- Takeoff / force metrics ---
        "vertical_velocity_at_takeoff_m_per_s": round(takeoff_velocity, 2),

        # --- Extra diagnostics / raw data ---
        "takeoff_time": round(t[takeoff_idx], 2),
        "start_time": round(t[start_idx], 2),
        "acceleration": list(a_inertial),
        "velocity": list(v),
        "time": list(t),
    }

