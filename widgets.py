'''Script to store functions for sliders and checkboxes.'''


from matplotlib.widgets import CheckButtons, Slider, Button
from constants import *
from pycbc.conversions import mchirp_from_mass1_mass2, spin1z_from_mass1_mass2_chi_eff_chi_a, spin2z_from_mass1_mass2_chi_eff_chi_a
from pycbc.conversions import mass1_from_mchirp_q, mass2_from_mchirp_q


# function to remove sliders (so they may be replaced with others)
def remove_sliders(slider_axes, sliders):
    for ax in slider_axes:
        ax.remove()
    for slider in sliders:
        slider.disconnect_events()
# instatiate detector 
det_state = {'det': 'H1'}
# function to make checkboxes
def make_checkboxes(fig):
    # make axes
    checkbox_ax = fig.add_axes(checkbox_rect)
    # checkbox labels
    chirp_q_label = r'Use $\mathcal{M}$ and $q$'
    plus_minus_label = r'Use $\chi_+$ and $\chi_-$'
    real_data_label = 'Use Real Data'
    det_label= 'Detector (L1, H1)'
    residual_label= 'Residuals'
    checkbox_labels = [chirp_q_label, plus_minus_label, real_data_label, det_label, residual_label]
    # checkboxes start unchecked
    init_status = [False, False, False, False, False]
    checkboxes = CheckButtons(checkbox_ax, checkbox_labels, init_status)

    #create buttons
    button_ax = fig.add_axes(button_signal)
    button_ax.set_visible(False)  # hidden initially
    buttons = Button(button_ax, 'GW150914', hovercolor='0.97' )

    button1_ax = fig.add_axes(button1_signal)
    button1_ax.set_visible(False)  # hidden initially
    buttons1 = Button(button1_ax, 'GW190521', hovercolor='0.97')

    button2_ax = fig.add_axes(button2_signal)
    button2_ax.set_visible(False)  # hidden initially
    buttons2 = Button(button2_ax, 'GW200129', hovercolor='0.97')


    button3_ax = fig.add_axes(button3_signal)
    button3_ax.set_visible(False)  # hidden initially
    buttons3 = Button(button3_ax, 'GW200224', hovercolor='0.97')

    button4_ax = fig.add_axes(button4_signal)
    button4_ax.set_visible(False)  # hidden initially
    buttons4 = Button(button4_ax, 'GW200311', hovercolor='0.97')

    button5_ax= fig.add_axes(button5_signal)
    button5_ax.set_visible(False)  #hidden initially
    buttons5= Button(button5_ax, 'GW191109', hovercolor= '0.97')

    button6_ax= fig.add_axes(button6_signal)
    button6_ax.set_visible(False)  #hidden initially
    buttons6= Button(button6_ax, 'GW190828', hovercolor= '0.97')

    button7_ax= fig.add_axes(button7_signal)
    button7_ax.set_visible(False) #hidden initially
    buttons7= Button(button7_ax, 'GW190519', hovercolor= '0.97')

    # Checkbox toggle 
    def on_checkbox_click(label):
        if label == real_data_label:
            idx = checkbox_labels.index(label)
            show_dropdown = checkboxes.get_status()[idx]
            button_ax.set_visible(show_dropdown)
            button1_ax.set_visible(show_dropdown)
            button2_ax.set_visible(show_dropdown)
            button3_ax.set_visible(show_dropdown)
            button4_ax.set_visible(show_dropdown)
            button5_ax.set_visible(show_dropdown)
            button6_ax.set_visible(show_dropdown)
            button7_ax.set_visible(show_dropdown)
            fig.canvas.draw_idle()
        
        elif label == det_label:
            idx = checkbox_labels.index(label)
            is_livingston = checkboxes.get_status()[idx]
            det_state['det'] = 'L1' if is_livingston else 'H1'
            


    checkboxes.on_clicked(on_checkbox_click)

    # Dropdown selection 
    def on_select(signal_name):
        print(f"Selected GW signal: {signal_name}")

    # connect buttons 
    buttons.on_clicked(on_select)
    buttons1.on_clicked(on_select)
    buttons2.on_clicked(on_select)
    buttons3.on_clicked(on_select)
    buttons4.on_clicked(on_select)
    buttons5.on_clicked(on_select)
    buttons6.on_clicked(on_select)
    buttons7.on_clicked(on_select)

    return checkboxes, buttons, buttons1, buttons2, buttons3, buttons4, buttons5, buttons6, buttons7


# function to make sliders
def make_sliders(fig, checkboxes, true_comp_params, init_comp_params= None):
    # unpack true parameter values
    m1_true, m2_true, chi1_true, chi2_true = true_comp_params
    #unpack initial parameter values
    if init_comp_params is not None:
        m1_init, m2_init, chi1_init, chi2_init= init_comp_params
    else: 
        m1_init= np.random.uniform(m1_true - 10, m1_true + 10)
        m2_init= np.random.uniform(m2_true - 10, m2_true + 10)
        chi1_init= np.random.uniform(chi1_min, chi1_max)
        chi2_init= np.random.uniform(chi2_min, chi2_max)
    chirp_init = mchirp_from_mass1_mass2(m1_init, m2_init)
    ratio_init = m2_init / m1_init
    spin_plus_init = chi_eff(m1_init, m2_init, chi1_init, chi2_init)
    spin_minus_init = chi_a(m1_init, m2_init, chi1_init, chi2_init)

    # get status of checkboxes
    chirp_q_checked, plus_minus_checked, real_data_checked, det_checked, residual_checked = checkboxes.get_status()
    # make axes for sliders
    ax1 = fig.add_axes(slider1_rect)
    ax2 = fig.add_axes(slider2_rect)
    ax3 = fig.add_axes(slider3_rect)
    ax4 = fig.add_axes(slider4_rect)
    ax5 = fig.add_axes(slider5_rect)
    ax6 = fig.add_axes(slider6_rect)
    
    # make sliders
    if chirp_q_checked:     
        chirp_true = mchirp_from_mass1_mass2(m1_true, m2_true)
        slider1 = Slider(ax=ax1, label=chirp_label, valmin=chirp_true - 10, valmax=chirp_true + 10, valinit= chirp_init, color= 'C2')
        slider2 = Slider(ax=ax2, label=ratio_label, valmin=ratio_min, valmax=ratio_max, valinit=ratio_init,  color= 'C2')
    else:
        slider1 = Slider(ax=ax1, label=m1_label, valmin=m1_true - 10, valmax=m1_true + 10, valinit= m1_init, color= 'C2')
        slider2 = Slider(ax=ax2, label=m2_label, valmin=m2_true - 10, valmax=m2_true + 10, valinit= m2_init,  color= 'C2')
    if plus_minus_checked:
        slider3 = Slider(ax=ax3, label=spin_plus_label, valmin=spin_plus_min, valmax=spin_plus_max, valinit= spin_plus_init,  color= 'C2')
        slider4 = Slider(ax=ax4, label=spin_minus_label, valmin=spin_minus_min, valmax=spin_minus_max, valinit= spin_minus_init,  color= 'C2')
    else:
        slider3 = Slider(ax=ax3, label=chi1_label, valmin=chi1_min, valmax=chi1_max, valinit= chi1_init,  color= 'C2')
        slider4 = Slider(ax=ax4, label=chi2_label, valmin=chi2_min, valmax=chi2_max, valinit= chi2_init,  color= 'C2')
    
    slider5 = Slider(ax=ax5, label=amp_label, valmin=1e-22, valmax=1e-24, valinit= 5e-23,  color= '0.65')
    slider6 = Slider(ax=ax6, label=phase_label, valmin= -np.pi, valmax= np.pi, valinit= 0,  color= '0.65')
    # store sliders and axes
    slider_axes = [ax1, ax2, ax3, ax4, ax5, ax6]
    sliders = [slider1, slider2, slider3, slider4, slider5, slider6]
    # remove tick marking initial position of sliders
    for slider in sliders:
        slider.ax.get_lines()[0].set_visible(False)
        slider.label.set_fontsize(4)
    return [slider_axes, sliders]


# make button to go to correct (or MAP) parameter values
def make_button(fig):
    button_ax = fig.add_axes(button_rect)
    return Button(button_ax, 'Go to Reference Parameters', hovercolor='0.975', fontsize=4)


# function to get component parameters from sliders and checkboxes
def get_comp_params(sliders):
    # convert slider parameters to component parameters
    if sliders[0].label.get_text() is chirp_label and sliders[2].label.get_text() is spin_plus_label:
        m1 = mass1_from_mchirp_q(sliders[0].val, 1./sliders[1].val)
        m2 = mass2_from_mchirp_q(sliders[0].val, 1./sliders[1].val)
        chi1 = spin1z_from_mass1_mass2_chi_eff_chi_a(m1, m2, sliders[2].val, sliders[3].val)
        chi2 = spin2z_from_mass1_mass2_chi_eff_chi_a(m1, m2, sliders[2].val, sliders[3].val)
    elif sliders[0].label.get_text() is chirp_label:
        m1 = mass1_from_mchirp_q(sliders[0].val, 1./sliders[1].val)
        m2 = mass2_from_mchirp_q(sliders[0].val, 1./sliders[1].val)
        chi1 = sliders[2].val
        chi2 = sliders[3].val
    elif sliders[2].label.get_text() is spin_plus_label:
        m1 = sliders[0].val
        m2 = sliders[1].val
        chi1 = spin1z_from_mass1_mass2_chi_eff_chi_a(m1, m2, sliders[2].val, sliders[3].val)
        chi2 = spin2z_from_mass1_mass2_chi_eff_chi_a(m1, m2, sliders[2].val, sliders[3].val)
    else:
        m1 = sliders[0].val
        m2 = sliders[1].val
        chi1 = sliders[2].val
        chi2 = sliders[3].val
    return np.array([m1, m2, chi1, chi2])


# function to get slider parameters from component parameters
def get_slider_params(params, checkboxes):
    # unpack parameter values
    m1, m2, chi1, chi2 = params.copy()
    # get status of checkboxes
    chirp_q_checked, plus_minus_checked, real_data_checked = checkboxes.get_status()
    if chirp_q_checked:
        params[0] = mchirp_from_mass1_mass2(m1, m2)
        params[1] = m2 / m1
    if plus_minus_checked:
        params[2] = chi_eff(m1, m2, chi1, chi2)
        params[3] = chi_a(m1, m2, chi1, chi2)
    return params


