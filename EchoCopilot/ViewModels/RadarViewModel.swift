// ViewModels/RadarViewModel.swift
// Echo Copilot — Radar tab state: setups list, search, filter, sort

import Foundation
import Observation

@Observable
final class RadarViewModel {
    // MARK: - State

    var setups: [TickerSetup] = []
    var searchText: String = ""
    var selectedFilter: RadarFilter = .all
    var selectedSort: SortOption = .actionableFirst
    var isLoading: Bool = false
    var errorMessage: String? = nil

    // MARK: - Dependencies (injected)

    private let repository: any SetupRepositoryProtocol
    private let settings: AppSettings

    init(repository: any SetupRepositoryProtocol, settings: AppSettings) {
        self.repository = repository
        self.settings = settings
        self.selectedSort = settings.preferredSortOption
    }

    // MARK: - Alert scheduling

    private func scheduleAlerts() {
        let current = setups
        let enabled = settings.enableMarketAlerts
        Task {
            await AlertService.shared.scheduleAlerts(for: current, enabled: enabled)
        }
    }

    // MARK: - Filtered + sorted setups

    var displayedSetups: [TickerSetup] {
        var result = setups

        // Apply filter
        switch selectedFilter {
        case .all:        break
        case .actionable: result = result.filter { $0.status == .actionable }
        case .shadow:     result = result.filter { $0.status == .shadow }
        case .main:       result = result.filter { $0.lane == .main }
        case .micro:      result = result.filter { $0.lane == .micro }
        }

        // Apply micro lane visibility
        if !settings.showMicroLane {
            result = result.filter { $0.lane != .micro }
        }

        // Apply search
        if !searchText.isEmpty {
            let q = searchText.uppercased()
            result = result.filter {
                $0.symbol.contains(q) || ($0.companyName?.uppercased().contains(q) == true)
            }
        }

        // Apply sort
        switch selectedSort {
        case .newest:
            result.sort { $0.timestamp > $1.timestamp }
        case .highestRVOL:
            result.sort { ($0.rvol ?? 0) > ($1.rvol ?? 0) }
        case .lowestSpread:
            result.sort { ($0.spreadPct ?? 999) < ($1.spreadPct ?? 999) }
        case .actionableFirst:
            result.sort {
                if $0.status != $1.status {
                    return $0.status == .actionable
                }
                return $0.timestamp > $1.timestamp
            }
        }

        return result
    }

    var actionableCount: Int { setups.filter { $0.status == .actionable }.count }
    var shadowCount: Int    { setups.filter { $0.status == .shadow }.count }

    // MARK: - Actions

    func load() async {
        isLoading = true
        errorMessage = nil
        do {
            setups = try await repository.fetchSetups()
        } catch {
            errorMessage = "Failed to load setups: \(error.localizedDescription)"
        }
        isLoading = false
        consumePendingFilter()
        scheduleAlerts()
    }

    /// Reads the filter set by ShowActionableSetupsIntent and applies it once.
    private func consumePendingFilter() {
        let key = "echo_pending_filter"
        guard let raw = UserDefaults.standard.string(forKey: key) else { return }
        UserDefaults.standard.removeObject(forKey: key)
        switch raw {
        case "actionable": selectedFilter = .actionable
        case "shadow":     selectedFilter = .shadow
        default:           selectedFilter = .all
        }
    }

    var refreshBanner: String? = nil   // Transient message shown after refresh

    func refresh() async {
        do {
            setups = try await repository.refresh()
            refreshBanner = nil
        } catch {
            refreshBanner = "Live data unavailable — showing cached prices."
        }
        scheduleAlerts()
    }
}
