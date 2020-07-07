import tkinter as tk
from config.config_cls import config as cfg_obj
import pickle
import logging
from tkinter import filedialog

def run_gui():

    """ Runs gui to configure a model-run and generate config object.

    Returns:
        instance of config class

    """

    config = cfg_obj()

    root = tk.Tk()
    root.title('Configure Model')

    root.configure(bg='white')

    ######### Only Enable Config When All Variables Are Defined ###########

    def myfunction(*args):

        """ Checks if the hemisphere and snow model have both been defined. If so, enables conf&exit button.

        Args:
            *args:

        Returns:
            no return, instead modifies button_quit object to enable
        """

        x = snow_model.get()
        y = hemisphere.get()
        custom_tracks = custom_tracks_bool.get()

        if x and y:
            button_quit.config(state='normal')
        else:
            button_quit.config(state='disabled')

        if custom_tracks:
            ct_sel.config(state='normal')
        else:
            ct_sel.config(state='disabled')


    def select_dir(text, name, file = False):

        """ Modifies config object to embed folder location of some data.
        """

        if file:
            f_name = filedialog.askopenfilename(title = text)
        else:
            f_name = filedialog.askdirectory(title = text,
                                             mustexist=True)

        setattr(config, name, f_name)

    ######### Year Choice ###########

    year_frame = tk.LabelFrame(root,
                          text='Select Year',
                          font=("Courier, 15"),
                          bg='white',
                          padx=5, pady=5)
    year_frame.grid(sticky='w',row=3,column=1, padx=10, pady=10)

    default_year = 2016
    year = tk.StringVar()
    year.set(f'{default_year}')
    tk.Entry(year_frame,
            bg='white',font=("Courier", 15),
             textvariable=year).pack(anchor='w')

    ######### Snow Model Choice ###########

    sm_frame = tk.LabelFrame(root,
                          text='Select Snow Model',
                          font=("Courier, 15"),
                          bg='white',
                          padx=5, pady=5)

    sm_frame.grid(sticky='w',row=2,column=1, padx=10, pady=10)

    MODES = [("SNOWPACK","snowpack"),
             ("NESOSIM-like","nesosim"),
             ("CPOM-like","degree_days")]

    snow_model = tk.StringVar()
    snow_model.trace_add('write', myfunction)
    for text, mode in MODES:
        tk.Radiobutton(sm_frame,
                       text=text,
                       bg='white',
                       font=("Courier", 15),
                       variable=snow_model, value=mode).pack(anchor='w')

    ######### Hemisphere Choice ###########

    hem_frame = tk.LabelFrame(root,
                          text='Select Hemisphere',
                          font=("Courier, 15"),
                          bg='white',
                          padx=5, pady=5)

    hem_frame.grid(sticky='w',row=1,column=1, padx=10, pady=10)


    hemispheres = [("Northern","nh"),
                   ("Southern","sh"),
                  ]

    hemisphere = tk.StringVar()
    hemisphere.trace_add('write', myfunction)

    for text, mode in hemispheres:
        tk.Radiobutton(hem_frame,
                       text=text,
                       bg='white',font=("Courier", 15),
                       variable=hemisphere,
                       value=mode).pack(anchor='w')


    ######### Configure SMRT ###########

    smrt_frame = tk.LabelFrame(root,
                          text='SMRT Options',
                          font=("Courier, 15"),
                          bg='white',
                          padx=5, pady=5)
    smrt_frame.grid(sticky='w',row=4,column=1, padx=10, pady=10)

    run_smrt = tk.BooleanVar(value=False)
    tk.Checkbutton(smrt_frame,
                   text='Run SMRT',
                    bg='white',font=("Courier", 15),
                   variable=run_smrt).pack(anchor='w')

    save_smrt = tk.BooleanVar(value=False)
    tk.Checkbutton(smrt_frame,
                   text='Save SMRT Input',
                    bg='white',font=("Courier", 15),
                   variable=save_smrt).pack(anchor='w')

    ######### Configure parralelisation ###########

    par_frame = tk.LabelFrame(root,
                          text='Parralelization Options',
                          font=("Courier, 15"),
                          bg='white',
                          padx=5, pady=5)
    par_frame.grid(sticky='w',row=1,column=2, padx=10, pady=10)

    def activateCheck():

        """Blocks out the entry box for number of cores if job_arrays check box is true"""

        if job_arrays.get() == 1:  # whenever checked
            num_cores_entry.config(state=tk.DISABLED)
        elif job_arrays.get() == 0:  # whenever unchecked
            num_cores_entry.config(state=tk.NORMAL)


    job_arrays = tk.BooleanVar(value=False)
    chk = tk.Checkbutton(par_frame, text='Job Arrays',
                            bg='white',font=("Courier", 15),
                         variable=job_arrays,
                         command = activateCheck,
                         ).pack(anchor='w')

    tk.Label(par_frame,
             text = 'Number of Cores',
             bg='white',font=("Courier", 15),).pack(anchor='w')

    num_cores = tk.StringVar()
    num_cores.set('1')
    num_cores_entry = tk.Entry(par_frame,
                bg='white',font=("Courier", 15),
                textvariable=num_cores)
    num_cores_entry.pack(anchor='w')


    gen_frame = tk.LabelFrame(root,
                          text='File Name Formats',
                          font=("Courier, 15"),
                          bg='white',
                          padx=5, pady=5)

    gen_frame.grid(sticky='w',row=2,column=2, padx=10, pady=10, )

    ######### Enter Log File Name ##########

    log_f_name = tk.StringVar()
    log_f_name.set('log.txt')
    tk.Label(gen_frame,
             text = 'Log File:',
             bg='white',font=("Courier", 15),).pack(anchor='w')
    tk.Entry(gen_frame,
                bg='white',font=("Courier", 15),
             textvariable=log_f_name).pack(anchor='w')

    ######### Enter Output File Name ##########



    output_f_name = tk.StringVar()
    output_f_name.set(f'output.h5')
    tk.Label(gen_frame,
             text = 'Output File:',
             bg='white',font=("Courier", 15),).pack(anchor='w')
    tk.Entry(gen_frame,
                bg='white',font=("Courier", 15),
             textvariable=output_f_name).pack(anchor='w')


    ######### Select Logging Level ##########

    log_lvl_frame = tk.LabelFrame(root,
                          text='Log Level',
                          font=("Courier, 15"),
                          bg='white',
                          padx=5, pady=5)
    log_lvl_frame.grid(sticky='w',row=3,column=2, padx=10, pady=10)

    log_level = tk.StringVar()
    log_level.set('Warning')

    log_level_dropdown = tk.OptionMenu(log_lvl_frame, log_level, 'Debug', 'Warning')
    log_level_dropdown.pack()


    ######## Select Custom Tracks File ##########

    custom_tracks_frame = tk.LabelFrame(root,
                          text='Log Level',
                          font=("Courier, 15"),
                          bg='white',
                          padx=5, pady=5)
    custom_tracks_frame.grid(sticky='w',row=4,column=2, padx=10, pady=10)

    custom_tracks_bool = tk.BooleanVar(value=False)
    custom_tracks_bool.trace_add('write', myfunction)
    ct_chk = tk.Checkbutton(custom_tracks_frame, text='Custom Tracks',
                            bg='white',font=("Courier", 15),
                             variable=custom_tracks_bool,
                             command = activateCheck,
                             ).pack(anchor='w')


    custom_tracks_sel = 'Select Custom Tracks'

    ct_sel = tk.Button(custom_tracks_frame,
              text=custom_tracks_sel,
              bg='white',font=("Courier", 15),
              command = lambda *args : select_dir('Select Custom Tracks',
                                                  'custom_input_list',
                                                  file=True),
              )

    ct_sel.pack(anchor='w')

##############################################################################################
################################################################################################


    def config_and_quit(config,
                        snow_model,
                        run_smrt,
                        save_smrt,
                        year,
                        output_f_name,
                        log_f_name,
                        log_level
                        ):

        """ Runs when config&exit button is pressed. Further configures config object, quits dialog and returns it.

        Args:
            snow_model: str tk_var with snow_model specification
            run_smrt: bool tk_var with SMRT specification
            year: tk_var with year of model run

        #TODO check dtype of year tk_var

        Returns:
            instance of config object
        """

        config.hemisphere = hemisphere.get()
        config.model_name = snow_model.get()
        config.run_smrt = run_smrt.get()
        config.year = int(year.get())
        config.save_micro_input = save_smrt.get()
        config.output_f_name = str(output_f_name.get())
        config.log_f_name= str(log_f_name.get())


        if log_level.get() == 'Warning':
            config.log_level = logging.WARNING
        elif log_level.get() == 'Debug':
            config.log_level = logging.DEBUG
        else:
            raise

        root.quit()

        return(config)

    button_quit = tk.Button(root,
                            text="Configure and exit",
                            font = ("Courier", 20),
                            command= lambda *args: config_and_quit(config,
                                                                   snow_model,
                                                                   run_smrt,
                                                                   save_smrt,
                                                                   year,
                                                                   output_f_name,
                                                                   log_f_name,
                                                                   log_level))

    myfunction()

    button_quit.grid(row=8,column=1, padx=10, pady=10, columnspan=2)

    root.mainloop()

    return(config)

def manual_config():

    config = cfg_obj()

    config.year = 2016
    config.log_f_name = 'log.txt'
    config.custom_input_list = False
    config.delete=True
    config.use_RAM = False
    config.log_level=logging.DEBUG
    config.model_name = 'degree_days' # can be 'snowpack', 'degree_days' or 'nesosim'
    config.results_f_name = 'result'
    config.run_smrt = False
    config.save_micro_input = False
    config.media_f_name = 'media'
    config.frequencies = [19e9, 37e9]

    return(config)

    #TODO get frequencies out of class def and into gui

if __name__ == '__main__':

    config = run_gui()
    # config = manual_config()

    pickle.dump(config, open('run.cfg', 'wb'))
