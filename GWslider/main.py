'''Main python file to run GW slider.'''



import matplotlib.pyplot as plt
from wave_gen import *
from widgets import *


# setup main plot
fig, ax = plt.subplots()

# adjust plot area
fig.subplots_adjust(left=0.3, bottom=0.3, right=0.95, top=0.95)

#chi-squared text box 
chi_text = fig.text(0.35, 0.35, r'$\chi^2=\frac{(d-f|d-f)}{(d|d)} = $' + str(0))

# make checkboxes
checkboxes = make_checkboxes(fig)

# make sliders
slider_axes, sliders = make_sliders(fig, checkboxes, params_random)

# make button to go to injected parameters
button = make_button(fig)

# get initial parameters
init_params = get_comp_params(sliders)

# plot data and fit
data_line, = ax.plot(times, waveform_inj, color='C1', label='data')
fit_line, = ax.plot(times, get_amp_phase_minimized_waveform(init_params, waveform_inj_FD), 
                    color='C0', label='fit')
ax.set_xlabel('time [s]')
ax.set_ylabel('strain')
ax.legend(loc='upper left')

# make error message if spins are outside domain
error_text = fig.text(0.05, 0.1, 'Spins not in domain.', transform=ax.transAxes, fontsize=10)
error_text.set_visible(False)

# function to handle checkbox changes
def checkbox_update(val):
    # store current parameter values
    global slider_axes, sliders
    param_vals = get_comp_params(sliders)
    # remove old sliders
    remove_sliders(slider_axes, sliders)
    # make new sliders
    slider_axes, sliders = make_sliders(fig, checkboxes, param_vals)
    # remove initial position ticks on each slider
    for slider in sliders:
        slider.ax.get_lines()[0].set_visible(False)
    # reattach slider_update to the new sliders
    sliders[0].on_changed(slider_update)
    sliders[1].on_changed(slider_update)
    sliders[2].on_changed(slider_update)
    sliders[3].on_changed(slider_update)
    # change data plotted
    if checkboxes.get_status()[2]:
        data_line.set_xdata(data_times)
        data_line.set_ydata(data_strains)
    else:
        data_line.set_xdata(times)
        data_line.set_ydata(waveform_inj)
    slider_update(val)
    fig.canvas.draw_idle()
    return

# function to handle slider changes
def slider_update(val):
    chirp_q_checked, plus_minus_checked, real_data_checked = checkboxes.get_status()
    # get component parameters
    params = get_comp_params(sliders)
    # check if spins are in domain
    if params[2] < chi1_min or params[2] > chi1_max or params[3] < chi2_min or params[3] > chi2_max:
        fit_line.set_ydata(np.zeros(num_times))
        error_text.set_visible(True)
        chi_text.set_visible(False)
    elif real_data_checked:
        fit= get_amp_phase_minimized_waveform(params, (intrp_waveform * waveform.sqrtSs)/A0)
        fit_line.set_ydata(fit)
        error_text.set_visible(False)
        chi_text.set_text(r'$\chi^2 = (d-h|d-h) = $' + str(normalized_chi_sq(intrp_strain,fit )))
    else:
        fit = get_amp_phase_minimized_waveform(params, waveform_inj_FD)
        fit_line.set_ydata(fit)
        error_text.set_visible(False)
        chi_text.set_text(r'$\chi^2 = (d-h|d-h) = $' + str(normalized_chi_sq(waveform_inj, fit)))
    fig.canvas.draw_idle()
    return

# function to send sliders to injected parameters
def button_push(event):
    # get status of checkboxes
    chirp_q_checked, plus_minus_checked, real_data_checked = checkboxes.get_status()
    # move sliders to injected value
    if chirp_q_checked and plus_minus_checked:
        sliders[0].set_val(chirp_inj)
        sliders[1].set_val(ratio_inj)
        sliders[2].set_val(spin_plus_inj)
        sliders[3].set_val(spin_minus_inj)
    elif chirp_q_checked:
        sliders[0].set_val(chirp_inj)
        sliders[1].set_val(ratio_inj)
        sliders[2].set_val(chi1_inj)
        sliders[3].set_val(chi2_inj)
    elif plus_minus_checked:
        sliders[0].set_val(m1_inj)
        sliders[1].set_val(m2_inj)
        sliders[2].set_val(spin_plus_inj)
        sliders[3].set_val(spin_minus_inj)
    else:
        sliders[0].set_val(m1_inj)
        sliders[1].set_val(m2_inj)
        sliders[2].set_val(chi1_inj)
        sliders[3].set_val(chi2_inj)
    slider_update(event)
    fig.canvas.draw_idle()
    return

# update plot as sliders move
sliders[0].on_changed(slider_update)
sliders[1].on_changed(slider_update)
sliders[2].on_changed(slider_update)
sliders[3].on_changed(slider_update)

# update plots when checkboxes changed
checkboxes.on_clicked(checkbox_update)

# update sliders when "to injected parameters" button pushed
button.on_clicked(button_push)

plt.show()

