// Views/Shared/ShareSheet.swift
// Echo Copilot — UIActivityViewController wrapper + URL identity helper

import SwiftUI

/// UIViewControllerRepresentable that presents a system share sheet for a file URL.
struct ShareSheet: UIViewControllerRepresentable {
    let url: URL

    func makeUIViewController(context: Context) -> UIActivityViewController {
        UIActivityViewController(activityItems: [url], applicationActivities: nil)
    }

    func updateUIViewController(_ uiViewController: UIActivityViewController, context: Context) {}
}

/// Identifiable URL wrapper so a URL can drive `.sheet(item:)`.
struct URLWrapper: Identifiable {
    let id = UUID()
    let url: URL
}
