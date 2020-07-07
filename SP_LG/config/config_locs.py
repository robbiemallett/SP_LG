import tkinter as tk
from tkinter import filedialog
from config.config_cls import config as cfg_obj
import pickle

def run_machine_gui():

    """ Runs gui to configure a model-run and generate config object.

    Returns:
        instance of config class

    """

    config = cfg_obj() #Makes an empty object

    returned_values = {}

    root = tk.Tk()
    root.title('Configure Model')

    root.configure(bg='white')

    ######### Only Enable Config When All Variables Are Defined ###########



    def select_dir(config, text, name, preview_label):

        """ Modifies config object to embed folder location of some data.
        """

        folder_name = filedialog.askdirectory(title = text,
                                              mustexist=True)

        preview_label.config(text=folder_name)

        setattr(config, name, folder_name)


    ######## Select Tracks Folder ##########

    folders_frame = tk.LabelFrame(root,
                          text='Select Folders',
                          font=("Courier, 15"),
                          bg='white',
                          padx=5, pady=5)

    folders_frame.grid(sticky='w',row=3,column=2, padx=10, pady=10, rowspan=2)

    tracks_text = 'Select Tracks Folder'
    tracks_name = 'tracks_dir'

    tk.Button(folders_frame,
              text=tracks_text,
                bg='white',font=("Courier", 15),
              command = lambda *args : select_dir(config, tracks_text, tracks_name, preview_label=tp),
              ).pack()

    tp = tk.Label(folders_frame)
    tp.pack()


    ######## Select Met Forcing Folder ##########

    met_text = 'Select Met Folder'
    met_name = 'met_dir'

    tk.Button(folders_frame,
              text=met_text,
              bg='white',font=("Courier", 15),
              command = lambda *args : select_dir(config, met_text, met_name, preview_label=met_preview),
              ).pack(anchor='w')

    met_preview = tk.Label(folders_frame)
    met_preview.pack()


    ######## Select Output Folder ##########

    output_text = 'Select Output Folder'
    output_name = 'output_dir'

    tk.Button(folders_frame,
              text=output_text,
              bg='white',font=("Courier", 15),
              command = lambda *args : select_dir(config, output_text, output_name, preview_label=output_preview),
              ).pack(anchor='w')

    output_preview = tk.Label(folders_frame)
    output_preview.pack()

    ######## Select Temporarty Folder ##########

    temp_text = 'Select Temporary Folder'
    temp_name = 'tmp_dir'

    tk.Button(folders_frame,
              text=temp_text,
              bg='white',font=("Courier", 15),
              command=lambda *args: select_dir(config, temp_text, temp_name, preview_label=temp_preview),
              ).pack(anchor='w')

    temp_preview = tk.Label(folders_frame)
    temp_preview.pack()

    ######################################################################################################

    button_quit = tk.Button(root,
                            text="Configure and exit",
                            font = ("Courier", 20),
                            command= lambda *args: root.quit())


    button_quit.grid(row=8,column=1, padx=10, pady=10, columnspan=2)

    root.mainloop()

    return(config)

def manual_gui():

    config = cfg_obj() #Makes an empty object

    # config.aux_data_dir = '/home/ucfarm0/SP_LG/aux_data/'
    # config.tracks_dir = '/home/ucfarm0/SP_LG/tracks/'
    # config.output_dir = '/home/ucfarm0/Scratch/'
    # config.hpc_run = True


    config.ram_dir = '/dev/shm/SP'
    config.tmp_dir = '/home/robbie/Dropbox/SP_LG/Snowpack_files'
    config.aux_data_dir = '/home/robbie/Dropbox/Data/SP_LG_aux_data/'
    config.output_dir = "/home/robbie/Dropbox/SP_LG/SP_LG_Output/"
    config.tracks_dir = "/home/robbie/Dropbox/SP_LG/tracks/"
    config.hpc_run = True

    return(config)

if __name__ == '__main__':

    # config = run_machine_gui()
    config = manual_gui()
    pickle.dump(config, open('desktop.cfg', 'wb'))
