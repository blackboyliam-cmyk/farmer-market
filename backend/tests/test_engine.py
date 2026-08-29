from app.services import validate_price_row
from app.services.profit import profit_for_market


def test_rejects_negative_price():
    cleaned, err = validate_price_row(
        {
            "state": "Maharashtra",
            "district": "Pune",
            "market": "Pune",
            "commodity": "Onion",
            "arrival_date": "01/01/2026",
            "min_price": -1,
            "max_price": 10,
            "modal_price": 5,
        }
    )
    assert cleaned is None
    assert "Negative" in err


def test_accepts_agmarknet_shape():
    cleaned, err = validate_price_row(
        {
            "state": "Maharashtra",
            "district": "Nashik",
            "market": "Lasalgaon",
            "commodity": "Onion",
            "variety": "Red",
            "arrival_date": "25/08/2026",
            "min_price": "1800",
            "max_price": "2200",
            "modal_price": "2000",
        }
    )
    assert err is None
    assert cleaned["modal_price"] == 2000.0
    assert cleaned["data_quality"] == "actual"


def test_profit_prefers_net_not_raw_price():
    # Higher raw price can lose after a longer, costlier trip.
    near = profit_for_market(4, 2100, 2000, 500, 0, 1.0, 0, 1)
    far = profit_for_market(4, 2350, 2000, 1700, 0, 1.0, 0, 1)
    assert far["price_used"] > near["price_used"]
    assert near["expected_net_profit"] > far["expected_net_profit"]


def test_break_even_and_roi():
    result = profit_for_market(
        yield_quintals=20,
        modal_price=2000,
        production_cost=20000,
        transport_cost=1000,
        storage_cost=0,
        market_charges_percent=1,
        area_hectares=1,
    )
    assert result["break_even_price"] > 0
    assert result["price_kind"] == "modal"
    assert result["expected_revenue"] == 40000
