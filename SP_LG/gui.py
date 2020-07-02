import tkinter as tk
import types
from tkinter import filedialog

def run_gui():

    config = types.SimpleNamespace() #Makes an empty object

    root = tk.Tk()
    root.title('Configure Model')

    root.configure(bg='white')

    ######### Only Enable Config When All Variables Are Defined ###########

    def myfunction(*args):
        x = snow_model.get()
        y = hemisphere.get()
        if x and y:
            button_quit.config(state='normal')
        else:
            button_quit.config(state='disabled')

    def select_dir(text, name):
        global config
        setattr(config, name, filedialog.askdirectory(title = text,
                                                      mustexist=True))

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
        if job_arrays.get() == 1:  # whenever checked
            a.config(state=tk.DISABLED)
        elif job_arrays.get() == 0:  # whenever unchecked
            a.config(state=tk.NORMAL)


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
    a = tk.Entry(par_frame,
                bg='white',font=("Courier", 15),
                textvariable=num_cores)
    a.pack(anchor='w')


    gen_frame = tk.LabelFrame(root,
                          text='File Name Formats',
                          font=("Courier, 15"),
                          bg='white',
                          padx=5, pady=5)

    gen_frame.grid(sticky='w',row=2,column=2, padx=10, pady=10, )

    ######### Enter Log File Name ##########

    log_f_name = tk.StringVar()
    log_f_name.set('log_*year*.txt')
    tk.Label(gen_frame,
             text = 'Log File:',
             bg='white',font=("Courier", 15),).pack(anchor='w')
    tk.Entry(gen_frame,
                bg='white',font=("Courier", 15),
             textvariable=log_f_name).pack(anchor='w')

    ######### Enter Output File Name ##########



    output_f_name = tk.StringVar()
    output_f_name.set(f'output_*year*.h5')
    tk.Label(gen_frame,
             text = 'Output File:',
             bg='white',font=("Courier", 15),).pack(anchor='w')
    tk.Entry(gen_frame,
                bg='white',font=("Courier", 15),
             textvariable=output_f_name).pack(anchor='w')

    ######## Select Tracks Folder ##########

    folders_frame = tk.LabelFrame(root,
                          text='Select Folders',
                          font=("Courier, 15"),
                          bg='white',
                          padx=5, pady=5)
    folders_frame.grid(sticky='w',row=3,column=2, padx=10, pady=10, rowspan=2)

    text = 'Select Tracks Folder'
    name = 'tracks_dir'

    tk.Button(folders_frame,
              text=text,
                bg='white',font=("Courier", 15),
              command = lambda *args : select_dir(text, name),
              ).pack(anchor='w')


    ######## Select Met Forcing Folder ##########

    text = 'Select Met Folder'
    name = 'met_dir'

    tk.Button(folders_frame,
              text=text,
              bg='white',font=("Courier", 15),
              command = lambda *args : select_dir(text, name),
              ).pack(anchor='w')


    ######## Select Output Folder ##########

    text = 'Select Output Folder'
    name = 'output_dir'

    tk.Button(folders_frame,
              text=text,
              bg='white',font=("Courier", 15),
              command = lambda *args : select_dir(text, name),
              ).pack(anchor='w')

    ######## Select Temporarty Folder ##########

    text = 'Select Temporary Folder'
    name = 'tmp_dir'

    tk.Button(folders_frame,
              text=text,
              bg='white',font=("Courier", 15),
              command = lambda *args : select_dir(text, name),
              ).pack(anchor='w')



    ######################################################################################################

    def config_and_quit(snow_model,
                        run_smrt,
                        year):
        global config
        config.hemisphere = hemisphere.get()
        config.snow_model = snow_model.get()
        config.run_smrt = run_smrt.get()
        config.year = int(year.get())
        root.quit()

    button_quit = tk.Button(root,
                            text="Configure and exit",
                            font = ("Courier", 20),
                            command= lambda *args: config_and_quit(snow_model,
                                                                   run_smrt,
                                                                   year))

    myfunction()

    button_quit.grid(row=8,column=1, padx=10, pady=10, columnspan=2)

    root.mainloop()

    print(config.snow_model, config.run_smrt)

    return(config)

if __name__ == '__main__':
    run_gui()