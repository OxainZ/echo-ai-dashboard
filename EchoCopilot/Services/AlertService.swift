// Services/AlertService.swift
// Echo Copilot — Schedules local UNUserNotifications at 9:25 AM ET for each
// actionable setup. Fires before market open so you have time to size up.
//
// Requirements: add NSUserNotificationUsageDescription to Info.plist.
// Usage: call requestPermission() on launch, scheduleAlerts(for:) after load.

import Foundation
import UserNotifications

@MainActor
final class AlertService {
    static let shared = AlertService()
    private init() {}

    private let center = UNUserNotificationCenter.current()
    private let idPrefix = "echo-setup-"
    private let et = TimeZone(identifier: "America/New_York")!

    // MARK: - Permission

    /// Asks iOS for notification permission. Call once at app launch.
    func requestPermission() async {
        try? await center.requestAuthorization(options: [.alert, .sound, .badge])
    }

    var isAuthorized: Bool {
        get async {
            let settings = await center.notificationSettings()
            return settings.authorizationStatus == .authorized
        }
    }

    // MARK: - Schedule

    /// Cancels all existing setup notifications, then schedules one per actionable
    /// setup for the next 9:25 AM Eastern weekday.
    func scheduleAlerts(for setups: [TickerSetup], enabled: Bool) async {
        // Always cancel stale ones first
        let existingIDs = await pendingSetupIDs()
        center.removePendingNotificationRequests(withIdentifiers: existingIDs)

        guard enabled else { return }
        guard await isAuthorized else { return }

        let actionable = setups.filter { $0.status == .actionable }
        guard !actionable.isEmpty else { return }

        var components = DateComponents()
        components.hour = 9
        components.minute = 25
        components.timeZone = et

        for setup in actionable {
            let content = UNMutableNotificationContent()
            content.title = "\(setup.symbol) — Actionable"
            content.body = notificationBody(for: setup)
            content.sound = .default
            content.userInfo = ["setupID": setup.id.uuidString, "symbol": setup.symbol]

            let trigger = UNCalendarNotificationTrigger(dateMatching: components, repeats: false)
            let request = UNNotificationRequest(
                identifier: idPrefix + setup.id.uuidString,
                content: content,
                trigger: trigger
            )
            try? await center.add(request)
        }
    }

    // MARK: - Cancel

    func cancelAll() {
        center.removeAllPendingNotificationRequests()
    }

    func cancel(setupID: UUID) {
        center.removePendingNotificationRequests(withIdentifiers: [idPrefix + setupID.uuidString])
    }

    // MARK: - Helpers

    private func pendingSetupIDs() async -> [String] {
        let pending = await center.pendingNotificationRequests()
        return pending.map(\.identifier).filter { $0.hasPrefix(idPrefix) }
    }

    private func notificationBody(for setup: TickerSetup) -> String {
        var parts: [String] = []
        if let trigger = setup.trigger {
            parts.append("Trigger \(trigger.asPrice)")
        }
        if let invalidation = setup.invalidation {
            parts.append("stop \(invalidation.asPrice)")
        }
        if let rvol = setup.rvol {
            parts.append(String(format: "RVOL %.1fx", rvol))
        }
        return parts.isEmpty ? "Market opens at 9:30 AM ET" : parts.joined(separator: " · ")
    }
}
