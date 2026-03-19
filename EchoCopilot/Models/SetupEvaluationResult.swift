// Models/SetupEvaluationResult.swift
// Echo Copilot — Output of the deterministic rules evaluator

import Foundation

struct SetupEvaluationResult {
    let evaluatedStatus: SetupStatus
    let shadowReasons: [ShadowReason]
    let passedChecks: [String]
    let failedChecks: [String]

    var isActionable: Bool { evaluatedStatus == .actionable }
}
