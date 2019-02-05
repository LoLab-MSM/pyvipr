from pysb import Model, Monomer, Parameter, Compartment, Rule, Initial

Model()

Parameter('vol_CYT', 1)
Parameter('vol_MOM', 1)

Compartment('CYT', parent=None, dimension=3, size=vol_CYT)
Compartment('MOM', parent=CYT, dimension=2, size=vol_MOM)

Monomer('tBid', ['bf'])
Monomer('Bax', ['bf', 's1', 's2', 'state'], {'state': ['I', 'A']})
Monomer('Bcl2', ['bf'])

Parameter('Bid_0', 40000.0)
Parameter('Bcl2_0', 20000.0)
Parameter('Bax_0', 80000.0)

Parameter('equilibrate_BidT_to_BidM_kf', 0.1)
Parameter('equilibrate_BidT_to_BidM_kr', 0.001)
Parameter('equilibrate_BaxC_to_BaxM_kf', 0.01)
Parameter('equilibrate_BaxC_to_BaxM_kr', 0.01)
Parameter('bind_BidM_Bcl2_kf', 1e-06)
Parameter('bind_BidM_Bcl2_kr', 0.06600000000000002)
Parameter('bind_BidM_BaxM_to_BidMBaxM_kf', 1e-07)
Parameter('bind_BidM_BaxM_to_BidMBaxM_kr', 0.001)
Parameter('catalyze_BidMBaxM_to_BidM_BaxA_kc', 1.0)

Initial(tBid(bf=None) ** CYT, Bid_0)
Initial(Bax(bf=None, s1=None, s2=None, state='I') ** CYT, Bax_0)
Initial(Bcl2(bf=None) ** MOM, Bcl2_0)

Rule('equilibrate_BidT_to_BidM', tBid(bf=None) ** CYT | tBid(bf=None) ** MOM, equilibrate_BidT_to_BidM_kf, equilibrate_BidT_to_BidM_kr)
Rule('equilibrate_BaxC_to_BaxM', Bax(bf=None, s1=None, s2=None, state='I') ** CYT | Bax(bf=None, s1=None, s2=None, state='I') ** MOM, equilibrate_BaxC_to_BaxM_kf, equilibrate_BaxC_to_BaxM_kr)
Rule('bind_BidM_BaxM_to_BidMBaxM', tBid(bf=None) ** MOM + Bax(bf=None, s1=None, s2=None, state='I') ** MOM | tBid(bf=1) ** MOM % Bax(bf=1, s1=None, s2=None, state='I') ** MOM, bind_BidM_BaxM_to_BidMBaxM_kf, bind_BidM_BaxM_to_BidMBaxM_kr)
Rule('catalyze_BidMBaxM_to_BidM_BaxA', tBid(bf=1) ** MOM % Bax(bf=1, s1=None, s2=None, state='I') ** MOM >> tBid(bf=None) ** MOM + Bax(bf=None, s1=None, s2=None, state='A') ** MOM, catalyze_BidMBaxM_to_BidM_BaxA_kc)
Rule('bind_BidM_Bcl2', tBid(bf=None) ** MOM + Bcl2(bf=None) ** MOM | tBid(bf=1) ** MOM % Bcl2(bf=1) ** MOM, bind_BidM_Bcl2_kf, bind_BidM_Bcl2_kr)
