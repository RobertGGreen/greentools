# -------------------------------
#| Robert Green   GFZ Potsdam    |
#| 2017-10-09                    |
# -------------------------------
def get_pazdictfrominventory(inventory,tr):
    ''' Reads an obspy station inventory object and
    for a given trace returns the obspy paz dictionary   
     '''
    inv=inventory.get_response(tr.id,tr.stats.starttime)
    polezerostage=inv.get_paz()
    totalsensitivity=inv.instrument_sensitivity
    pzdict={}
    pzdict['poles']=polezerostage.poles
    pzdict['zeros']=polezerostage.zeros
    pzdict['gain']=polezerostage.normalization_factor
    pzdict['sensitivity']=totalsensitivity.value
    return pzdict