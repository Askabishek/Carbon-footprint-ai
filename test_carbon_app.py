import pytest
from carbon_app import calculate_emissions

def test_calculate_emissions_zero():
    """Test with minimal/zero inputs."""
    res = calculate_emissions(0, 15.0, 0, 0, 0, "Vegan", "Most/All")
    # Driving: 0, Flights: 0, Energy: 0, Diet: 1.5, Waste: 0.1
    assert res["total"] == pytest.approx(1.6)

def test_calculate_emissions_average():
    """Test with typical average inputs."""
    res = calculate_emissions(10000, 15.0, 1, 0, 200, "Average (Meat/Veg)", "Some")
    # Driving: (10000/15)*2.31/1000 = 1.54
    # Flights: 1*0.15 = 0.15
    # Energy: (200*12*0.4)/1000 = 0.96
    # Diet: 2.5
    # Waste: 0.3
    # Total: 1.54 + 0.15 + 0.96 + 2.5 + 0.3 = 5.45
    assert res["total"] == pytest.approx(5.45)

def test_efficiency_edge_case():
    """Test efficiency edge case (division by zero prevention)."""
    res = calculate_emissions(1000, 0, 0, 0, 0, "Vegan", "Most/All")
    # Efficiency is capped at 0.1 internally
    # (1000/0.1)*2.31/1000 = 23.1
    assert res["driving"] == pytest.approx(23.1)

def test_diet_mapping():
    """Test different diet types."""
    res_vegan = calculate_emissions(0, 15, 0, 0, 0, "Vegan", "None")
    res_meat = calculate_emissions(0, 15, 0, 0, 0, "Meat-heavy", "None")
    assert res_meat["total"] > res_vegan["total"]
