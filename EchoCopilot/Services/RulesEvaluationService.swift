// Services/RulesEvaluationService.swift
// Echo Copilot — Deterministic rules engine for Actionable vs Shadow classification

import Foundation

// MARK: - Protocol

protocol RulesEvaluationServiceProtocol {
    func evaluate(setup: TickerSetup, settings: AppSettings) -> SetupEvaluationResult
}

// MARK: - Concrete evaluator

final class SetupRulesEvaluator: RulesEvaluationServiceProtocol {

    func evaluate(setup: TickerSetup, settings: AppSettings) -> SetupEvaluationResult {
        var reasons: [ShadowReason] = []
        var passed: [String] = []
        var failed: [String] = []

        let spreadThreshold = settings.spreadThreshold(for: setup.lane)
        let impactThreshold = settings.impactThreshold(for: setup.lane)

        // 1. Symbol present
        if setup.symbol.trimmingCharacters(in: .whitespaces).isEmpty {
            failed.append("Symbol missing")
            reasons.append(.other("Missing symbol"))
        } else {
            passed.append("Symbol: \(setup.symbol)")
        }

        // 2. Price present
        if setup.price == nil {
            failed.append("Price missing")
            reasons.append(.missingPrice)
        } else {
            passed.append("Price present: \(setup.price!.asPrice)")
        }

        // 3. Trigger present
        if setup.trigger == nil {
            failed.append("Trigger missing")
            reasons.append(.missingTrigger)
        } else {
            passed.append("Trigger: \(setup.trigger!.asPrice)")
        }

        // 4. Invalidation present
        if setup.invalidation == nil {
            failed.append("Invalidation missing")
            reasons.append(.missingInvalidation)
        } else {
            passed.append("Invalidation: \(setup.invalidation!.asPrice)")
        }

        // 5. Targets present
        if setup.target1 == nil || setup.target2 == nil {
            failed.append("Targets missing (need T1 and T2)")
            reasons.append(.missingTargets)
        } else {
            passed.append("Targets: T1=\(setup.target1!.asPrice), T2=\(setup.target2!.asPrice)")
        }

        // 6. Verified
        if !setup.isVerified {
            failed.append("Setup not verified")
            reasons.append(.missingVerification)
        } else {
            passed.append("Setup verified")
        }

        // 7. Halted
        if setup.halted {
            failed.append("Security is halted")
            reasons.append(.halted)
        } else {
            passed.append("Not halted")
        }

        // 8. SSR (warning, not blocking by itself — included in shadow reasons for transparency)
        if setup.ssrActive {
            failed.append("SSR active (short-side restricted)")
            reasons.append(.ssrRestriction)
        } else {
            passed.append("No SSR")
        }

        // 9. RVOL
        if let rvol = setup.rvol {
            if rvol >= settings.rvolThreshold {
                passed.append("RVOL \(rvol.asMultiplier) ≥ \(settings.rvolThreshold.asMultiplier)")
            } else {
                failed.append("RVOL \(rvol.asMultiplier) < \(settings.rvolThreshold.asMultiplier) threshold")
                reasons.append(.rvolTooLow)
            }
        } else {
            failed.append("RVOL missing")
            reasons.append(.rvolTooLow)
        }

        // 10. Vol-Z
        if let volZ = setup.volZ {
            if volZ >= settings.volZThreshold {
                passed.append("Vol-Z \(volZ.rounded2) ≥ \(settings.volZThreshold.rounded2)")
            } else {
                failed.append("Vol-Z \(volZ.rounded2) < \(settings.volZThreshold.rounded2) threshold")
                reasons.append(.volZTooLow)
            }
        } else {
            failed.append("Vol-Z missing")
            reasons.append(.volZTooLow)
        }

        // 11. Spread
        if let spread = setup.spreadPct {
            if spread <= spreadThreshold {
                passed.append("Spread \(spread.asPercent) ≤ \(spreadThreshold.asPercent) threshold")
            } else {
                failed.append("Spread \(spread.asPercent) > \(spreadThreshold.asPercent) (\(setup.lane.rawValue) threshold)")
                reasons.append(.spreadTooWide)
            }
        } else {
            passed.append("Spread not provided (unchecked)")
        }

        // 12. Impact % ADTV (only checked when provided)
        if let impact = setup.impactPctADTV {
            if impact <= impactThreshold {
                passed.append("Impact \(impact.asPercent) ≤ \(impactThreshold.asPercent) threshold")
            } else {
                failed.append("Impact \(impact.asPercent) > \(impactThreshold.asPercent) (\(setup.lane.rawValue) threshold)")
                reasons.append(.impactTooHigh)
            }
        }

        let isActionable = failed.isEmpty && reasons.isEmpty
        let status: SetupStatus = isActionable ? .actionable : .shadow

        return SetupEvaluationResult(
            evaluatedStatus: status,
            shadowReasons: reasons,
            passedChecks: passed,
            failedChecks: failed
        )
    }
}
