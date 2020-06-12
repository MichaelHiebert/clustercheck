from enum import Enum
from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image
import os
import random
import numpy as np
from numpy.random import default_rng
from functools import partial
from datetime import datetime

def get_timestamp_string():
    dt = datetime.now()
    return '{}-{}-{}_{}:{}:{}'.format(dt.year,dt.month,dt.day,dt.hour,dt.minute,dt.second)

class DisplayState(Enum):
    DIR_LEVEL = 0
    SUBDIR_LEVEL = 1

class Display:
    def __init__(self, master_dir):
        self.master_dir = master_dir

        self.seen = set()
        
        name = self.master_dir.split('/')[-1]
        self.filename = 'data/{}.txt'.format(name)
        # create our file
        try:
            with open(self.filename, 'x'):
                pass
        except:
            self.seen = self._load_from_file(self.filename)

        self.state = DisplayState.DIR_LEVEL
        self.directory = self._choose_random_directory(self.master_dir)

        if self.directory == False:
            raise RuntimeError('Directory has no available clusters!')
        else:
            self.seen.add(self.directory)

        self.width = 600
        self.height = 600
        self.num_rows = 5
        self.num_cols = 5

        self._set_mainframe()

        self._set_dirframe()

        self.root.protocol('WM_DELETE_WINDOW', self._handle_close)
        self.root.mainloop()

    def _load_from_file(self, fname):
        with open(fname) as f:
            l = f.readlines()

        return set([x for x in l if x[0] == '*'])

    def _choose_random_directory(self, master_dir):
        cluster_dirs = ['{}/{}'.format(self.master_dir, d) for d in next(os.walk(master_dir))[1]]

        available = set(cluster_dirs).difference(self.seen)

        if len(available) == 0: # no more available folders!
            return False

        return random.choice(list(available))

    def _handle_close(self):
        # TODO save all
        self.root.destroy()

    def _set_mainframe(self):
        """
            Sets the root and main frame of the GUI
        """

        self.root = Tk()
        self.title = 'Cluster Checker'
        self.root.minsize(width=self.width, height=self.height)

        self.mainframe = ttk.Frame(self.root, padding="3 3 12 12")
        self.mainframe.grid(column=0, row=0, sticky=NS)

    def _get_files_from_dir(self, d):
        return [f for f in os.listdir(d) if os.path.isfile(os.path.join(d, f))]

    def _get_image_spread(self, upper_bound=25):
        rng = default_rng()

        ims = self._get_files_from_dir(self.directory)
        self.images = ['{}/{}'.format(self.directory, im) for im in ims]
        idx = rng.choice(len(ims), size=min(len(ims),upper_bound), replace=False)

        return list(np.array(self.images)[idx])

    def _start_eval(self, filepath):
        self.model_face = filepath
        self.state = DisplayState.SUBDIR_LEVEL

        self.results = list()

        self.root.title('Are these from the same cluster?')

        self._set_subdirframe(0)

    def _set_subdirframe(self, ix):
        """
            Sets the subdirectory view frame of the GUI
        """

        if ix >= len(self.images):
            self._new_cluster()
            return

        imwidth = self.width
        imheight = self.height

        self.subdirframe = ttk.Frame(master=self.mainframe, borderwidth=2, relief=GROOVE)
        self.subdirframe.grid(column=0, row=0, sticky=NSEW)

        model_img = ImageTk.PhotoImage(Image.open(self.model_face).resize((imwidth, imheight)))
        model = ttk.Label(master=self.subdirframe, image=model_img)
        model.image = model_img
        model.grid(column=0, row=0, sticky=NSEW)

        comp_img = ImageTk.PhotoImage(Image.open(self.images[ix]).resize((imwidth, imheight)))
        comp = ttk.Label(master=self.subdirframe, image=comp_img)
        comp_img.image = comp_img
        comp.grid(column=1, row=0, sticky=NSEW)

        no = Button(master=self.subdirframe, text='NO', height=10, command=partial(self._no, ix))
        no.grid(column=0, row=1, sticky=NSEW)

        yes = Button(master=self.subdirframe, text='YES', height=10, command=partial(self._yes, ix))
        yes.grid(column=1, row=1, sticky=NSEW)

    def _yes(self, ix):
        self.results.append(True)
        self._set_subdirframe(ix+1)

    def _no(self, ix):
        self.results.append(False)
        self._set_subdirframe(ix+1)

    def _save_eval(self, ims, res):
        wrong = [x[0] for x in zip(self.images, self.results) if not x[1]]
        with open(self.filename, 'a') as f:
            f.write('*' + self.directory + '\n')
            f.writelines('\n'.join(wrong))
            f.write('\n')

    def _new_cluster(self):
        # SAVE WORK
        self._save_eval(self.images, self.results)

        self.state = DisplayState.DIR_LEVEL
        self.directory = self._choose_random_directory(self.master_dir)

        if self.directory == False:
            print('No new clusters to classify')
            self._handle_close()
            return
            # raise RuntimeError('Directory has no available clusters!')
        else:
            self.seen.add(self.directory)

        self._set_dirframe()

    def _set_dirframe(self):
        """
            Sets the directory view frame of the GUI
        """

        num_cols = self.num_cols
        num_rows = self.num_rows

        imwidth = self.width // num_cols
        imheight = self.width // num_rows

        self.root.title('Please select the image that you believe represents this cluster')

        self.dirframe = ttk.Frame(master=self.mainframe, borderwidth=2, relief=GROOVE)
        self.dirframe.grid(column=0, row=0, sticky='NSEW')

        self.imgs = ttk.Frame(master=self.dirframe, borderwidth=1)
        self.imgs.grid(column=0, columnspan=num_cols, row=0, rowspan=num_rows, sticky=NSEW)

        impaths = self._get_image_spread(upper_bound = num_cols * num_rows)

        fdict = {}

        for row in range(num_rows):
            for col in range(num_cols):
                ix = int(row * num_rows + col)

                if ix >= len(impaths):
                    setattr(self, 'grid_{}{}'.format(row, col), ttk.Button(master=self.imgs))
                    getattr(self, 'grid_{}{}'.format(row, col)).grid(column=col, columnspan=1, row=row, rowspan=1, sticky=NSEW)
                else:
                    img_path = impaths[ix]
                    image = ImageTk.PhotoImage(Image.open(img_path).resize((imwidth, imheight)))
                    setattr(self, 'grid_{}{}'.format(row, col), ttk.Button(master=self.imgs, image=image, command=partial(self._start_eval, img_path)))
                    getattr(self, 'grid_{}{}'.format(row, col)).grid(column=col, columnspan=1, row=row, rowspan=1, sticky=NSEW)
                    getattr(self, 'grid_{}{}'.format(row, col)).image=image

class MetaDisplay:
    def __init__(self, cluster_interface, trust=75):
        self.ci = cluster_interface
        self.trust = trust

        self.width = 600
        self.height = 600
        self.num_rows = 5
        self.num_cols = 5

        self._set_mainframe()

        self._set_subdirframe()


        self.root.protocol('WM_DELETE_WINDOW', self._handle_close)
        self.root.mainloop()

    def _choose_random_directory(self, master_dir):
        cluster_dirs = ['{}/{}'.format(self.master_dir, d) for d in next(os.walk(master_dir))[1]]

        available = set(cluster_dirs).difference(self.seen)

        if len(available) == 0: # no more available folders!
            return False

        return random.choice(list(available))

    def _handle_close(self):
        t = get_timestamp_string()
        self.ci.save(t)
        print('Saved to {}.json'.format(t))
        self.root.destroy()

    def _set_mainframe(self):
        """
            Sets the root and main frame of the GUI
        """

        self.root = Tk()
        self.title = 'Cluster Checker'
        self.root.minsize(width=self.width, height=self.height)

        self.mainframe = ttk.Frame(self.root, padding="3 3 12 12")
        self.mainframe.grid(column=0, row=0, sticky=NS)

    def _set_subdirframe(self):
        """
            Sets the subdirectory view frame of the GUI
        """
        check_self = random.randint(0, 100) > self.trust

        c = self.ci.clusters

        self.ci.set_potency()
        self.root.title('Do these belong to the same cluster? Potency: {}'.format(self.ci.potency))
        if check_self:
            cluster,_ = self.ci.suggest_intra_pairing()

            imwidth = self.width
            imheight = self.height

            im1,im2 = self.ci.get_node_name_from_cluster(cluster),self.ci.get_node_name_from_cluster(cluster)

            self.subdirframe = ttk.Frame(master=self.mainframe, borderwidth=2, relief=GROOVE)
            self.subdirframe.grid(column=0, row=0, sticky=NSEW)
            
            model_img = ImageTk.PhotoImage(Image.open(im1).resize((imwidth, imheight)))
            model = ttk.Label(master=self.subdirframe, image=model_img)
            model.image = model_img
            model.grid(column=0, row=0, sticky=NSEW)

            comp_img = ImageTk.PhotoImage(Image.open(im2).resize((imwidth, imheight)))
            comp = ttk.Label(master=self.subdirframe, image=comp_img)
            comp_img.image = comp_img
            comp.grid(column=1, row=0, sticky=NSEW)

            no = Button(master=self.subdirframe, text='NO', height=10, command=partial(self.ci.problem_with_cluster, cluster, im1, im2, self._set_subdirframe))
            no.grid(column=0, row=1, sticky=NSEW)

            yes = Button(master=self.subdirframe, text='YES', height=10, command=self._set_subdirframe)
            yes.grid(column=1, row=1, sticky=NSEW)
        else:
            pairing = self.ci.suggest_pairing()

            if pairing is False:
                self.subdirframe = ttk.Frame(master=self.mainframe, borderwidth=2, relief=GROOVE)
                self.subdirframe.grid(column=0,row=0,sticky=NSEW)
                self.label = ttk.Label(master=self.subdirframe, text='No more available clusters. Please exit, (this will save automatically).')
                self.label.grid(column=0,row=0,sticky=NSEW)
            else:
                im1,im2 = pairing

                imwidth = self.width
                imheight = self.height

                self.subdirframe = ttk.Frame(master=self.mainframe, borderwidth=2, relief=GROOVE)
                self.subdirframe.grid(column=0, row=0, sticky=NSEW)

                model_img = ImageTk.PhotoImage(Image.open(self.ci.get_node_name_from_cluster(im1)).resize((imwidth, imheight)))
                model = ttk.Label(master=self.subdirframe, image=model_img)
                model.image = model_img
                model.grid(column=0, row=0, sticky=NSEW)

                comp_img = ImageTk.PhotoImage(Image.open(self.ci.get_node_name_from_cluster(im2)).resize((imwidth, imheight)))
                comp = ttk.Label(master=self.subdirframe, image=comp_img)
                comp_img.image = comp_img
                comp.grid(column=1, row=0, sticky=NSEW)

                no = Button(master=self.subdirframe, text='NO', height=10, command=partial(self.ci.is_bad_pairing, im1, im2, self._set_subdirframe))
                no.grid(column=0, row=1, sticky=NSEW)

                yes = Button(master=self.subdirframe, text='YES', height=10, command=partial(self.ci.is_good_pairing, im1, im2, self._set_subdirframe))
                yes.grid(column=1, row=1, sticky=NSEW)

if __name__ == "__main__":
    # root = Tk()  
    # canvas = Canvas(root, width = 300, height = 300)  
    # canvas.pack()  
    # img = ImageTk.PhotoImage(Image.open("ball.png"))  
    # canvas.create_image(20, 20, anchor=NW, image=img) 
    # root.mainloop() 

    master = '/Users/michaelhiebert/Development/clustercheck/data/test'
    d = Display(master)

    print('hello')
