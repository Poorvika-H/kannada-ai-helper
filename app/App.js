import React, { useState, useRef } from "react";
import {
  View, Text, TextInput, TouchableOpacity, FlatList,
  StyleSheet, ActivityIndicator, KeyboardAvoidingView, Platform, SafeAreaView,
} from "react-native";

// CHANGE THIS: your laptop's IP on the same Wi-Fi as your phone
// (Windows: run `ipconfig` and look for IPv4 Address)
const BACKEND_URL = "http://192.168.1.10:8000";

const UI = {
  kn: {
    title: "ನಿಮ್ಮ ಸಹಾಯಕ",
    hint: "ನಿಮ್ಮ ಪ್ರಶ್ನೆ ಇಲ್ಲಿ ಬರೆಯಿರಿ",
    send: "ಕಳುಹಿಸಿ",
    empty: "ನಿಮಗೆ ಏನು ತಿಳಿಯಬೇಕು? ಕೇಳಿ.",
    error: "ಏನೋ ತೊಂದರೆ ಆಯಿತು. ಇಂಟರ್ನೆಟ್ ನೋಡಿ, ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.",
  },
  en: {
    title: "Study Helper",
    hint: "Type your question here",
    send: "Send",
    empty: "What would you like to learn today?",
    error: "Something went wrong. Check your internet and try again.",
  },
};

export default function App() {
  const [lang, setLang] = useState("kn");
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const listRef = useRef(null);
  const t = UI[lang];

  const switchLang = (next) => {
    setLang(next);
    setMessages([]); // fresh chat when the language changes
  };

  const send = async () => {
    const text = input.trim();
    if (!text || loading) return;

    const history = [...messages, { role: "user", content: text }];
    setMessages(history);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`${BACKEND_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ lang, messages: history }),
      });
      const data = await res.json();
      setMessages([...history, { role: "assistant", content: data.reply }]);
    } catch (e) {
      setMessages([...history, { role: "assistant", content: t.error }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={s.screen}>
      <View style={s.header}>
        <Text style={s.title}>{t.title}</Text>
        <View style={s.toggle}>
          {["kn", "en"].map((code) => (
            <TouchableOpacity
              key={code}
              onPress={() => switchLang(code)}
              style={[s.toggleBtn, lang === code && s.toggleOn]}
            >
              <Text style={[s.toggleText, lang === code && s.toggleTextOn]}>
                {code === "kn" ? "ಕನ್ನಡ" : "English"}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === "ios" ? "padding" : undefined}
      >
        <FlatList
          ref={listRef}
          data={messages}
          keyExtractor={(_, i) => String(i)}
          contentContainerStyle={{ padding: 16, flexGrow: 1 }}
          onContentSizeChange={() => listRef.current?.scrollToEnd()}
          ListEmptyComponent={<Text style={s.empty}>{t.empty}</Text>}
          renderItem={({ item }) => (
            <View style={[s.bubble, item.role === "user" ? s.user : s.bot]}>
              <Text style={[s.msg, item.role === "user" && { color: "#fff" }]}>
                {item.content}
              </Text>
            </View>
          )}
        />
        {loading && <ActivityIndicator size="large" color="#1F5C4A" style={{ margin: 8 }} />}

        <View style={s.inputRow}>
          <TextInput
            style={s.input}
            value={input}
            onChangeText={setInput}
            placeholder={t.hint}
            multiline
          />
          <TouchableOpacity style={s.sendBtn} onPress={send} disabled={loading}>
            <Text style={s.sendText}>{t.send}</Text>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const GREEN = "#1F5C4A";
const s = StyleSheet.create({
  screen: { flex: 1, backgroundColor: "#FBF8F1" },
  header: {
    backgroundColor: GREEN, padding: 16, paddingTop: 28,
    flexDirection: "row", justifyContent: "space-between", alignItems: "center",
  },
  title: { color: "#fff", fontSize: 24, fontWeight: "700" },
  toggle: { flexDirection: "row", backgroundColor: "#174638", borderRadius: 24 },
  toggleBtn: { paddingVertical: 8, paddingHorizontal: 14, borderRadius: 24 },
  toggleOn: { backgroundColor: "#F2B544" },
  toggleText: { color: "#cfe3da", fontSize: 16 },
  toggleTextOn: { color: "#1b1b1b", fontWeight: "700" },
  empty: { fontSize: 22, color: "#555", textAlign: "center", marginTop: 80 },
  bubble: { maxWidth: "88%", padding: 14, borderRadius: 16, marginBottom: 12 },
  user: { alignSelf: "flex-end", backgroundColor: GREEN },
  bot: { alignSelf: "flex-start", backgroundColor: "#fff", borderWidth: 1, borderColor: "#e3dccb" },
  msg: { fontSize: 19, lineHeight: 28, color: "#1b1b1b" },
  inputRow: { flexDirection: "row", padding: 12, gap: 8, alignItems: "flex-end" },
  input: {
    flex: 1, backgroundColor: "#fff", borderWidth: 1, borderColor: "#d6cfbd",
    borderRadius: 14, padding: 12, fontSize: 19, maxHeight: 120,
  },
  sendBtn: { backgroundColor: GREEN, paddingVertical: 14, paddingHorizontal: 18, borderRadius: 14 },
  sendText: { color: "#fff", fontSize: 18, fontWeight: "700" },
});
