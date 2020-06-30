class degree_days_snowpack():

    def __init__(self, depth=0):

        self.SWE = 0

        self.dep = 0

    def accumulate(self,
                   amount):

        rho_s = 350
        rho_w = 1023

        self.SWE = self.SWE + amount

        self.dep = self.dep + amount * (rho_w / rho_s)

    def total(self,
              variable):

        if variable == 'SWE':
            return (self.SWE)

        elif variable == 'dep':
            return (self.dep)

        else:
            raise
