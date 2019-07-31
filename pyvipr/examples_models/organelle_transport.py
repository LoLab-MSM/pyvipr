from pysb import *

Model()

Parameter('NA', 6.02e23)
Parameter('kp_LR', 4e8)
Parameter('km_LR', 10)
Parameter('k_LRtrans', 1000)
Parameter('kp_LT1', 4e8)
Parameter('km_LT1', 10)
Parameter('k_LT1trans', 1000)
Parameter('kp_L2T2', 4e8)
Parameter('km_L2T2', 10)
Parameter('k_L2T2trans', 1000)
Parameter('vol_CYT', 1)
Parameter('vol_O1M', 1)
Parameter('vol_O1V', 1)
Parameter('vol_O2M', 1)
Parameter('vol_O2V', 1)
Parameter('L_0', 1000)
Parameter('R_0', 200)
Parameter('T1_0', 1000)
Parameter('T2_0', 1000)

Compartment('CYT', parent=None, dimension=3, size=vol_CYT)
Compartment('OM1', parent=CYT, dimension=2, size=vol_O1M)
Compartment('OV1', parent=OM1, dimension=3, size=vol_O1V)
Compartment('OM2', parent=CYT, dimension=2, size=vol_O2M)
Compartment('OV2', parent=OM2, dimension=3, size=vol_O2V)

Monomer('L')
Monomer('R')
Monomer('LR')
Monomer('T1')
Monomer('LT1')
Monomer('L2')
Monomer('T2')
Monomer('L2T2')

Initial(L() ** CYT, L_0)
Initial(R() ** OM1, R_0)
Initial(T1() ** OM1, T1_0)
Initial(T2() ** OM2, T2_0)

Rule('bind_L_R', L() ** CYT + R() ** OM1 | LR() ** OM1, kp_LR, km_LR)
Rule('L_transport_OV1', LR() ** OM1 >> L() ** OV1 + R() ** OM1, k_LRtrans)
Rule('bind_L_T1', L() ** OV1 + T1() ** OM1 | LT1() ** OM1, kp_LT1, km_LT1)
Rule('create_L2', LT1() ** OM1 >> T1() ** OM1 + L2() ** CYT, k_LT1trans)
Rule('bind_L2_T2', L2() ** CYT + T2() ** OM2 | L2T2() ** OM2, kp_L2T2, km_L2T2)
Rule('L2_transport_OV2', L2T2() ** OM2 >> T2() ** OM2 + L2() ** OV2, k_L2T2trans)

# L@CYT + R@O1M <-> LR@O1M kp_LR, km_LR
# LR@O1M -> L@O1V + R@O1M k_LRtrans
# L@O1V + T1@O1M <-> LT1@O1M kp_LT1, km_LT1
# LT1@O1M -> T1@O1M + L2@CYT k_LT1trans
# L2@CYT + T2@O2M <-> L2T2@O2M kp_L2T2, km_L2T2
# L2T2@O2M -> T2@O2M + L2@O2V k_L2T2trans