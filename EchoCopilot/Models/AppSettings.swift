// Models/AppSettings.swift
// Echo Copilot — User-configurable settings with sensible defaults

import Foundation

struct AppSettings: Codable {
    // Spread thresholds (percent)
    var mainLaneSpreadThreshold: Double = 0.35
    var microLaneSpreadThreshold: Double = 0.25

    // Volume quality thresholds
    var rvolThreshold: Double = 1.5
    var volZThreshold: Double = 1.0

    // Risk sizing
    var defaultRiskPercent: Double = 1.0

    // Impact thresholds (percent of ADTV)
    var impactThresholdMain: Double = 0.50
    var impactThresholdMicro: Double = 0.30

    // Display
    var showMicroLane: Bool = true
    var preferredSortOption: SortOption = .actionableFirst

    // AI features
    var enableFoundationModels: Bool = true

    // Notifications — fires at 9:25 AM ET for each actionable setup
    var enableMarketAlerts: Bool = true

    // Note: Polygon API key is stored in Keychain via KeychainService, not here.

    // MARK: - Spread threshold for a given lane
    func spreadThreshold(for lane: TradingLane) -> Double {
        lane == .main ? mainLaneSpreadThreshold : microLaneSpreadThreshold
    }

    // MARK: - Impact threshold for a given lane
    func impactThreshold(for lane: TradingLane) -> Double {
        lane == .main ? impactThresholdMain : impactThresholdMicro
    }
}
