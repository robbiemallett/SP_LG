class nesosim_snowpack():

    def __init__(self):

        init_dict = {'new': 0,
                     'old': 0,
                     'tot': 0}

        self.SWE = init_dict

        self.dep = init_dict

    def accumulate(self,
                   amount):

        rho_n = 200
        rho_o = 350
        rho_w = 1023

        self.SWE['new'] = self.SWE['new'] + amount

        self.dep['new'] = self.dep['new'] + amount * (rho_w / rho_n)

    def wind_pack(self):

        rho_n = 200;
        rho_o = 350;
        rho_w = 1023

        alpha = 6.264e-3

        self.dep = {'new': self.dep['new'] - alpha * self.dep['tot'],

                    'old': self.dep['old'] + (rho_n / rho_o) * alpha * self.dep['tot'],

                    'tot': self.dep['new'] - alpha * self.dep['tot']
                           + self.dep['old'] + (rho_n / rho_o) * alpha * self.dep['tot']}

        self.SWE = {'new': self.dep['new'] * (rho_n / rho_w),

                    'old': self.dep['old'] * (rho_o / rho_w),

                    'tot': self.dep['new'] * (rho_n / rho_w)
                           + self.dep['old'] * (rho_o / rho_w)}

    def total(self,
              variable):

        if variable == 'SWE':
            return (self.SWE['tot'])
        elif variable == 'dep':
            return (self.dep['tot'])
        else:
            raise
