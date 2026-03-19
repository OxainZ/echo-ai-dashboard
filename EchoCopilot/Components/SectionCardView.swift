// Components/SectionCardView.swift
// Echo Copilot — Grouped section container with title and content

import SwiftUI

struct SectionCardView<Content: View>: View {
    let title: String
    var systemImage: String? = nil
    @ViewBuilder let content: Content

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(spacing: 6) {
                if let icon = systemImage {
                    Image(systemName: icon)
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(.accent)
                }
                Text(title.uppercased())
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(.secondary)
            }
            content
        }
        .padding(14)
        .background(Color(.systemGray6), in: RoundedRectangle(cornerRadius: 14))
    }
}

#Preview {
    SectionCardView(title: "Key Levels", systemImage: "target") {
        MetricRowView(label: "Trigger", value: "491.10", highlight: true, valueColor: .green)
        MetricRowView(label: "Invalidation", value: "475.00", highlight: true, valueColor: .red)
    }
    .padding()
    .background(.black)
}
