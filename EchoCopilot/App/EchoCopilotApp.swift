// App/EchoCopilotApp.swift
// Echo Copilot — App entry point

import SwiftUI

@main
struct EchoCopilotApp: App {
    @StateObject private var environment = AppEnvironment()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(environment)
                .preferredColorScheme(.dark)
                .task {
                    await AlertService.shared.requestPermission()
                }
        }
    }
}
