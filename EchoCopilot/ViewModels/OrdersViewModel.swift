// ViewModels/OrdersViewModel.swift
// Echo Copilot — Manual order calculator: position sizing with validation

import Foundation
import Observation

@Observable
final class OrdersViewModel {
    // MARK: - Form inputs (String for text fields)

    var entryPriceText: String = ""
    var stopPriceText: String = ""
    var targetPriceText: String = ""
    var accountSizeText: String = "50000"
    var riskPercentText: String = "1.0"
    var selectedTicker: String = ""

    // MARK: - Validation

    var validationError: String? {
        guard let entry = entryPrice, entry > 0 else { return "Enter a valid entry price" }
        guard let stop = stopPrice, stop > 0 else { return "Enter a valid stop price" }
        guard let target = targetPrice, target > 0 else { return "Enter a valid target price" }
        guard let account = accountSize, account > 0 else { return "Enter a valid account size" }
        guard let risk = riskPercent, risk > 0 && risk <= 100 else { return "Risk % must be 0–100" }
        if abs(entry - stop) < 0.001 { return "Stop price must differ from entry" }
        return nil
    }

    /// Non-blocking warnings (show in orange, don't block calculation).
    var positionWarning: String? {
        guard let calc = calculation else { return nil }
        if calc.totalPositionCost > calc.accountSize {
            let pct = (calc.totalPositionCost / calc.accountSize * 100)
            return String(format: "Position notional (%.0f%% of account) exceeds account size — consider reducing risk %%.", pct)
        }
        return nil
    }

    var rrWarning: String? {
        guard let calc = calculation, calc.rewardToRisk > 0 else { return nil }
        if calc.rewardToRisk < 2.0 {
            return String(format: "R:R is only %.2f:1 — aim for ≥ 2:1 before entering.", calc.rewardToRisk)
        }
        return nil
    }

    // MARK: - Parsed doubles

    var entryPrice: Double?  { Double(entryPriceText.replacingOccurrences(of: ",", with: "")) }
    var stopPrice: Double?   { Double(stopPriceText.replacingOccurrences(of: ",", with: "")) }
    var targetPrice: Double? { Double(targetPriceText.replacingOccurrences(of: ",", with: "")) }
    var accountSize: Double? { Double(accountSizeText.replacingOccurrences(of: ",", with: "")) }
    var riskPercent: Double? { Double(riskPercentText) }

    // MARK: - Computed calculation

    var calculation: OrderCalculation? {
        guard validationError == nil,
              let entry = entryPrice,
              let stop = stopPrice,
              let target = targetPrice,
              let account = accountSize,
              let risk = riskPercent
        else { return nil }

        return OrderCalculation(
            entryPrice: entry,
            stopPrice: stop,
            targetPrice: target,
            accountSize: account,
            riskPercent: risk
        )
    }

    // MARK: - Stop presets

    func applyStopPreset(pct: Double) {
        guard let entry = entryPrice else { return }
        let stop = entry * (1 - pct / 100)
        stopPriceText = String(format: "%.2f", stop)
    }

    // MARK: - Copy order summary

    var orderSummaryText: String {
        guard let calc = calculation else { return "Complete the form to generate an order summary." }
        return """
        \(selectedTicker.isEmpty ? "TICKER" : selectedTicker) ORDER SUMMARY
        Entry: \(calc.entryPrice.asPrice)
        Stop: \(calc.stopPrice.asPrice)
        Target: \(calc.targetPrice.asPrice)
        Account: \(calc.accountSize.asCurrency)
        Risk %: \(calc.riskPercent.asPercent)
        Dollar Risk: \(calc.dollarRisk.asCurrency)
        Risk/Share: \(calc.riskPerShare.asPrice)
        Shares: \(calc.positionSizeShares)
        Notional: \(calc.totalPositionCost.asCurrency)
        R:R: \(String(format: "%.2f", calc.rewardToRisk))
        Proj. Profit: \(calc.projectedProfit.asCurrency)
        """
    }

    // MARK: - Load from setup

    func load(from setup: TickerSetup, settings: AppSettings) {
        selectedTicker = setup.symbol
        entryPriceText = setup.trigger?.asPrice ?? setup.price?.asPrice ?? ""
        stopPriceText = setup.invalidation?.asPrice ?? ""
        targetPriceText = setup.target1?.asPrice ?? ""
        riskPercentText = String(settings.defaultRiskPercent)
    }
}
