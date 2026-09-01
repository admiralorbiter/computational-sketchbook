import math
from utils.fees import compute_fee, FeeInput, ProductType, Role

def test_taker_fee_general_mid():
    fin = FeeInput(price=0.50, contracts=1)
    fee = compute_fee(fin, Role.taker, ProductType.general)
    assert math.isclose(fee, 0.02, rel_tol=0, abs_tol=1e-9)

def test_taker_fee_nasdaq_mid():
    fin = FeeInput(price=0.50, contracts=1)
    fee = compute_fee(fin, Role.taker, ProductType.nasdaq_spx)
    assert math.isclose(fee, 0.01, rel_tol=0, abs_tol=1e-9)

def test_maker_fee_sports_mid():
    fin = FeeInput(price=0.50, contracts=1)
    fee = compute_fee(fin, Role.maker, ProductType.sports)
    assert math.isclose(fee, 0.01, rel_tol=0, abs_tol=1e-9)
