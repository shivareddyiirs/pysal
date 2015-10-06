import copy
import registry as sr
from pysal.weights import W
import patsy as p
from numpy import array, ndarray, asarray
from six import iteritems as diter

def pandashandler(formula_like, data):
    """
    process a pysal model signature and convert an equation/formula pair into a
    pysal-specific object
    """
    if '||' in formula_like:
        mu, inst = formula_like.split('||')
        y, X = p.dmatrices(mu + '-1' , data=data)
        yend, q  = p.dmatrices(inst + '-1', data=data)
        rargs = [y,X,yend,q]
        rargs = [asarray(i) for i in rargs]
    else:
        y, X = p.dmatrices(formula_like + '-1', data=data)
        rargs = [asarray(y), asarray(X)]

    return rargs

#def model(eqn, *args, data=df, **kwargs)
class Model(object):
    """
    le model manager
    
    arguments that sit above the pysal model API:

    mtype : string mapping to the function called from spreg
    fit : Bool denoting whether to actually apply the mtype to the data provided
          immediately.

    an example call would look like:

        >>> Model(y,X,W, mtype='ML_Lag')
        >>> Model(y,X,W, mytpe='OLS_Regimes')
    """
    def __init__(self, *args, **kwargs):
        mtype = kwargs.pop('mtype', sr.user['OLS'])
        self._mtype = mtype
        if isinstance(mtype, str):
            mtype = sr.__all__[mtype] 
        self._fit = kwargs.pop('fit', True)

        if isinstance(args[0], str):
            formula = args[0]
            data = kwargs.pop('data')
            matrices = pandashandler(formula, data)
        elif 'formula' in kwargs.keys() and 'data' in kwargs.keys():
            formula = kwargs.pop('formula')
            data = kwargs.pop('data')
            matrices = pandashandler(formula, data)
        else:
            matrices = [arg for arg in args if not isinstance(arg, W)]
        
        args = matrices + [arg for arg in args if isinstance(arg, W)]

        if self._fit:
            self._called = mtype(*args, **kwargs)
            for name in dir(self._called):
                exec('self.{n} = self._called.{n}'.format(n=name))

#need to still pass names down from formula into relevant pysal arguments

if __name__ == '__main__':
    import pysal as ps

    dbf = ps.open(ps.examples.get_path('columbus.dbf'))
    y, X = dbf.by_col_array(['HOVAL']), dbf.by_col_array(['INC', 'CRIME'])
    W = ps.open(ps.examples.get_path('columbus.gal')).read()
    mod1 = sr.OLS(y,X)
    hmod1 = Model(y,X)

    mod2 = sr.OLS(y,X,W)
    hmod2 = Model(y,X,W)

    mod3 = sr.ML_Lag(y,X,W)
    hmod3 = Model(y,X,W, mtype='ML_Lag')

    mod4 = sr.ML_Error(y,X,W)
    hmod4 = Model(y,X,W,mtype='ML_Error')

    #real power comes from this, though
    import geopandas as gpd
    
    df = gpd.read_file(ps.examples.get_path('columbus.dbf'))

    hmod1_pd = Model('HOVAL ~ INC + CRIME', data=data)
    mod5 = sr.TSLS('HOVAL ~ INC + CRIME')
