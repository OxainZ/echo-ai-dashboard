// Services/CopyTicketService.swift
// Echo Copilot — Formats the exact Copy Ticket text for Fidelity handoff

import Foundation

final class CopyTicketService {

    func ticketText(for setup: TickerSetup) -> String {
        let na = "N/A"

        let shadowText: String
        if setup.shadowReasons.isEmpty {
            shadowText = "None"
        } else {
            shadowText = setup.shadowReasons.map { $0.description }.joined(separator: ", ")
        }

        return """
        \(setup.symbol)
        Status: \(setup.status.rawValue)
        Lane: \(setup.lane.rawValue)
        Verified: \(setup.isVerified ? "Yes" : "No")
        Price: \(setup.price?.asPrice ?? na)
        PMH: \(setup.pmh.asPrice)
        PDH: \(setup.pdh.asPrice)
        PDL: \(setup.pdl?.asPrice ?? na)
        Trigger: \(setup.trigger?.asPrice ?? na)
        Invalidation: \(setup.invalidation?.asPrice ?? na)
        Target 1: \(setup.target1?.asPrice ?? na)
        Target 2: \(setup.target2?.asPrice ?? na)
        Spread: \(setup.spreadPct?.asPercent ?? na)
        RVOL: \(setup.rvol?.asMultiplier ?? na)
        Vol-Z: \(setup.volZ?.rounded2 ?? na)
        Impact % ADTV: \(setup.impactPctADTV?.asPercent ?? na)
        Cash Compliance: \(setup.cashCompliance.rawValue)
        Catalyst: \(setup.catalystSummary ?? na)
        Shadow Reasons: \(shadowText)
        Notes: \(setup.notes.isEmpty ? na : setup.notes)
        """
    }
}
