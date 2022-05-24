import math

def norm_dist(x=0,u=0,s=1,cum=False):
    if cum == False:
        answer = (1/(s*math.sqrt(2*math.pi)))*math.exp(-.5*(((x-u)/s)**2))
    else:
        answer = math.erf(x / math.sqrt(2.0))
        answer = (1.0 + answer) / 2.0
    return answer

class Options:
    def __init__(self,price = None,rfr=0.0,div=0.0,time=365.0,vol=20.0,strike=100.0,spot=100.0,call=True):
        self.price = price
        self.rfr = rfr/100
        self.div = div/100
        self.time = time/365
        self.vol = vol/100
        self.strike = strike
        self.spot = spot
        self.call = call
        self.d1 = (1/(self.vol*math.sqrt(self.time)))*(math.log(self.spot/self.strike)+(self.rfr-self.div+(self.vol**2)/2)*self.time)
        self.d2 = self.d1 - self.vol*math.sqrt(self.time)
    def BSM_Price(self,vol=None):
        if vol == None:
            vol = self.vol
        d1 = (1/(vol*math.sqrt(self.time)))*(math.log(self.spot/self.strike)+(self.rfr-self.div+(vol**2)/2)*self.time)
        d2 = d1 - vol*math.sqrt(self.time)
        a = self.spot*math.exp(-self.div*self.time)
        b = math.exp(-self.rfr*self.time)*self.strike
        if self.call == True:
            price = a*norm_dist(x=d1,cum=True) -b*norm_dist(x=d2,cum=True)
        elif self.call == False:
            price = b*norm_dist(x=-d2,cum=True) - a*norm_dist(x=-d1,cum=True)
        return price
    def BSM_PutCallParity(self):
        a = -self.spot+self.strike*math.exp(-self.rfr*self.time)
        if self.price is not None:
            if self.call == True:
                pcp = self.price + a
            elif self.call == False:
                pcp = self.price - a
        else:
            if self.call == True:
                pcp = self.BSM_Price() + a
            elif self.call == False:
                pcp = self.BSM_Price() - a
        return pcp
    def BSM_Delta(self):
        a = math.exp(-self.div*self.time)
        if self.call == True:
            delta = a*norm_dist(x=self.d1,cum=True)
        elif self.call == False:
            delta = -a*norm_dist(x=-self.d1,cum=True)
        return delta
    def BSM_Vega(self,vol=None):
        if vol == None:
            vol = self.vol
        d1 = (1/(vol*math.sqrt(self.time)))*(math.log(self.spot/self.strike)+(self.rfr-self.div+(vol**2)/2)*self.time)
        return (self.spot*math.exp(-self.div*self.time)*norm_dist(x=d1,cum=False)*math.sqrt(self.time))/100
    def BSM_Theta(self):
        a = math.exp(-self.div*self.time)*\
            ((self.spot*norm_dist(x=self.d1,cum=False)*self.vol)/
             (2*math.sqrt(self.time)))
        b = self.rfr*self.strike*math.exp((-self.rfr*self.time))\
            *norm_dist(x=self.d2,cum=True)
        c = self.div*self.spot*math.exp(-self.div*self.time)\
            *norm_dist(x=self.d1,cum=True)
        if self.call == True:
            theta = -a-b+c
        elif self.call == False:
            theta = -a+b-c
        return theta/365 # Note this is to show the daily theta decay
    def BSM_Rho(self):
        a = self.strike*self.time*math.exp(-self.rfr*self.time)
        if self.call == True:
            rho = a*norm_dist(x=self.d2,cum=True)
        elif self.call == False:
            rho = -a*norm_dist(x=-self.d2,cum=True)
        return rho/100
    def BSM_Epsilon(self):
        a = self.spot*self.time*math.exp(-self.div*self.time)
        if self.call == True:
            epsilon = -a*norm_dist(x=self.d1,cum=True)
        elif self.call == False:
            epsilon = a*norm_dist(x=-self.d1,cum=True)
        return epsilon
    def BSM_Lambda(self):
        return self.BSM_Delta()*(self.spot/self.BSM_Price())
    def BSM_Gamma(self):
        return math.exp(-self.div*self.time)*norm_dist(x=self.d1,cum=False)\
               /(self.spot*self.vol*math.sqrt(self.time))
    def BSM_Vanna(self):
        return math.exp(-self.div*self.time)*norm_dist(x=self.d1,cum=False)\
               *(self.d2/self.vol)
    def BSM_Charm(self):
        a = self.div*math.exp(-self.div*self.time)
        b = math.exp(-self.div*self.time)*norm_dist(x=self.d1,cum=False)* \
            ((2*(self.rfr-self.div)*self.time-self.d2*self.vol*math.sqrt(self.time))
             /(2*self.time*self.vol.math.sqrt(self.time)))
        if self.call == True:
            charm = a*norm_dist(x=self.d1,cum=True)-b
        elif self.call == False:
            charm = -a*norm_dist(x=-self.d1,cum=True)-b
        return charm
    def BSM_IV(self):
        if self.call == False:
            cp = self.BSM_PutCallParity()
        else:
            cp = self.price
        iv = .0000000001
        b = 1
        for a in range(1,11):
            b = b/10
            while True:
                dif = cp - self.BSM_Price(iv)
                if dif > 0:
                    iv += b
                else:
                    iv -= b
                    break
        return iv
    @staticmethod
    def BSM_Calc_RFR(cPrice,pPrice,spot,strike,time):
        return (math.exp((1+(cPrice-pPrice-spot)/strike)*(time/365)))**(365/time)-1
testcase = Options(call=True,strike=100,rfr=3.5)
print(testcase.BSM_Price())
print(testcase.BSM_PutCallParity())
print(testcase.BSM_Calc_RFR(testcase.BSM_Price(),testcase.BSM_PutCallParity(),100,100,1))





