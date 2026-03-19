// Services/ExplanationService.swift
// Echo Copilot — Explanation service (deterministic fallback + Foundation Models when available)

import Foundation

// MARK: - Protocol

protocol ExplanationServiceProtocol {
    func explain(setup: TickerSetup, evaluation: SetupEvaluationResult) async -> ExplanationResult
}

// MARK: - Deterministic fallback (always available)

final class DeterministicExplanationService: ExplanationServiceProtocol {
    func explain(setup: TickerSetup, evaluation: SetupEvaluationResult) async -> ExplanationResult {
        let statusWord = evaluation.isActionable ? "Actionable" : "Shadow"

        let headline: String
        if evaluation.isActionable {
            headline = "\(setup.symbol) passes all rules — marked Actionable (\(setup.lane.rawValue) lane)"
        } else {
            headline = "\(setup.symbol) is Shadow — \(evaluation.shadowReasons.count) condition(s) not met"
        }

        var bodyParts: [String] = []

        // Trigger / invalidation summary
        if let trigger = setup.trigger, let inv = setup.invalidation {
            bodyParts.append("Entry trigger is \(trigger.asPrice); setup invalidates below \(inv.asPrice).")
        } else if let inv = setup.invalidation {
            bodyParts.append("Invalidation set at \(inv.asPrice). No trigger confirmed yet.")
        } else {
            bodyParts.append("Trigger and/or invalidation not yet defined.")
        }

        // Target summary
        if let t1 = setup.target1, let t2 = setup.target2 {
            bodyParts.append("Targets: T1 at \(t1.asPrice), T2 at \(t2.asPrice).")
        }

        // Volume quality
        if let rvol = setup.rvol, let volZ = setup.volZ {
            bodyParts.append("Volume quality: RVOL \(rvol.asMultiplier), Vol-Z \(volZ.rounded2).")
        }

        // Catalyst
        if let cat = setup.catalystSummary, !cat.isEmpty {
            bodyParts.append("Catalyst: \(cat).")
        }

        // Shadow summary
        if !evaluation.isActionable {
            let reasonList = evaluation.shadowReasons.map { $0.description }.joined(separator: "; ")
            bodyParts.append("Blocked by: \(reasonList).")
        }

        let riskNote: String
        if let entry = setup.price, let inv = setup.invalidation {
            let riskPts = abs(entry - inv)
            riskNote = "Price \(entry.asPrice) vs invalidation \(inv.asPrice) = \(riskPts.asPrice) pts risk. Size accordingly."
        } else {
            riskNote = "Set stop at your invalidation level before sizing."
        }

        return ExplanationResult(
            headline: headline,
            body: bodyParts.joined(separator: " "),
            passedChecks: evaluation.passedChecks,
            failedChecks: evaluation.failedChecks,
            riskNote: riskNote,
            usedAI: false
        )
    }
}

// MARK: - Foundation Models implementation (iOS 26+ only)
// Guarded with @available so it compiles on earlier SDKs too.
// The factory in AppEnvironment chooses the right implementation at runtime.

@available(iOS 26, *)
final class FoundationModelsExplanationService: ExplanationServiceProtocol {
    func explain(setup: TickerSetup, evaluation: SetupEvaluationResult) async -> ExplanationResult {
        // Build a structured prompt from the setup data
        let prompt = buildPrompt(setup: setup, evaluation: evaluation)

        do {
            // Use Foundation Models LanguageModelSession
            // NOTE: Requires the "Foundation Models" capability in your app's entitlements.
            // If the model is not available on this device, we fall back to deterministic.
            let session = try FoundationModels.LanguageModelSession()
            let response = try await session.respond(to: prompt)
            let text = response.content

            // Parse the AI response into our structured result
            return ExplanationResult(
                headline: "\(setup.symbol) — AI Analysis",
                body: text,
                passedChecks: evaluation.passedChecks,
                failedChecks: evaluation.failedChecks,
                riskNote: "Review all levels before entering. AI output is informational only.",
                usedAI: true
            )
        } catch {
            // Graceful fallback — no crash
            let fallback = DeterministicExplanationService()
            return await fallback.explain(setup: setup, evaluation: evaluation)
        }
    }

    private func buildPrompt(setup: TickerSetup, evaluation: SetupEvaluationResult) -> String {
        var parts: [String] = [
            "You are a concise trade analyst. Evaluate this setup in 3-4 sentences.",
            "Ticker: \(setup.symbol)",
            "Status: \(evaluation.evaluatedStatus.rawValue)",
            "Lane: \(setup.lane.rawValue)",
        ]
        if let p = setup.price { parts.append("Price: \(p.asPrice)") }
        if let t = setup.trigger { parts.append("Trigger: \(t.asPrice)") }
        if let i = setup.invalidation { parts.append("Invalidation: \(i.asPrice)") }
        if let t1 = setup.target1 { parts.append("Target 1: \(t1.asPrice)") }
        if let t2 = setup.target2 { parts.append("Target 2: \(t2.asPrice)") }
        if let rvol = setup.rvol { parts.append("RVOL: \(rvol.asMultiplier)") }
        if let cat = setup.catalystSummary { parts.append("Catalyst: \(cat)") }
        if !evaluation.failedChecks.isEmpty {
            parts.append("Failed: \(evaluation.failedChecks.joined(separator: ", "))")
        }
        parts.append("Be direct. Focus on setup quality, key levels, and risk.")
        return parts.joined(separator: "\n")
    }
}

// MARK: - Factory

enum ExplanationServiceFactory {
    static func make(enableAI: Bool) -> any ExplanationServiceProtocol {
        if enableAI, #available(iOS 26, *) {
            return FoundationModelsExplanationService()
        }
        return DeterministicExplanationService()
    }
}
