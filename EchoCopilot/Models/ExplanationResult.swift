// Models/ExplanationResult.swift
// Echo Copilot — Result returned by ExplanationService

import Foundation

struct ExplanationResult {
    let headline: String
    let body: String
    let passedChecks: [String]
    let failedChecks: [String]
    let riskNote: String
    /// True when Apple Intelligence / Foundation Models was used; false for deterministic fallback.
    let usedAI: Bool
}
