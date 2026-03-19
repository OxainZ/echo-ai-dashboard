// Components/CopyButtonView.swift
// Echo Copilot — Copy button with brief "Copied!" feedback

import SwiftUI

struct CopyButtonView: View {
    let text: String
    let label: String
    var icon: String = "doc.on.doc"

    @State private var copied = false

    var body: some View {
        Button {
            ClipboardHelper.copy(text)
            withAnimation {
                copied = true
            }
            DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                withAnimation { copied = false }
            }
        } label: {
            HStack(spacing: 6) {
                Image(systemName: copied ? "checkmark" : icon)
                Text(copied ? "Copied!" : label)
            }
            .font(.subheadline.weight(.semibold))
            .foregroundStyle(copied ? .green : .white)
            .padding(.horizontal, 16)
            .padding(.vertical, 10)
            .background(copied ? Color.green.opacity(0.2) : Color.accentColor, in: RoundedRectangle(cornerRadius: 10))
        }
        .buttonStyle(.plain)
        .animation(.easeInOut(duration: 0.2), value: copied)
    }
}

#Preview {
    CopyButtonView(text: "Sample ticket text", label: "Copy Ticket", icon: "doc.on.doc")
        .padding()
        .background(.black)
}
