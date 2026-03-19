// Models/OrderCalculation.swift
// Echo Copilot — Computed position sizing result (value type, no side effects)

import Foundation

struct OrderCalculation {
    let entryPrice: Double
    let stopPrice: Double
    let targetPrice: Double
    let accountSize: Double
    let riskPercent: Double

    // MARK: - Computed outputs

    var dollarRisk: Double {
        accountSize * (riskPercent / 100.0)
    }

    var riskPerShare: Double {
        abs(entryPrice - stopPrice)
    }

    var positionSizeShares: Int {
        guard riskPerShare > 0 else { return 0 }
        return Int(dollarRisk / riskPerShare)
    }

    var totalPositionCost: Double {
        Double(positionSizeShares) * entryPrice
    }

    var rewardToRisk: Double {
        guard riskPerShare > 0 else { return 0 }
        return abs(targetPrice - entryPrice) / riskPerShare
    }

    var projectedProfit: Double {
        Double(positionSizeShares) * abs(targetPrice - entryPrice)
    }

    // MARK: - Validation

    var isValid: Bool {
        entryPrice > 0 && stopPrice > 0 && targetPrice > 0 && accountSize > 0
            && riskPercent > 0 && riskPerShare > 0
    }
}
