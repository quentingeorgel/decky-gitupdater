import React from "react";
import {
  definePlugin,
  PanelSection,
  PanelSectionRow,
  ButtonItem,
  staticClasses,
} from "@decky/ui";
import { callable } from "@decky/api";
import { useEffect, useState } from "react";
import { FaGithub } from "react-icons/fa";

const getRepos = callable<[], string>("get_repos");
const saveRepos = callable<[string], boolean>("save_repos");
const checkAll = callable<[], any[]>("check_all");
const install = callable<[string, string, string], any>("install");

function Content() {
  const [text, setText] = useState("");
  const [statuses, setStatuses] = useState<any[]>([]);
  const [busy, setBusy] = useState<string | null>(null);

  useEffect(() => {
    getRepos().then((t) => setText(t || ""));
  }, []);

  const handleSaveAndCheck = async () => {
    await saveRepos(text);
    setBusy("check");
    try {
      const res = await checkAll();
      setStatuses(res);
    } finally {
      setBusy(null);
    }
  };

  const handleInstall = async (s: any) => {
    setBusy(s.name);
    try {
      const r = await install(s.repo, s.remote, s.name);
      if (!r.success) {
        alert(`Erreur : ${r.error}`);
      }
      setStatuses(await checkAll());
    } finally {
      setBusy(null);
    }
  };

  return (
    <>
      <PanelSection title="Dépôts GitHub">
        <PanelSectionRow>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder={
              "owner/repo\n" +
              "owner/repo@v1.2.3\n" +
              "owner/repo#nom_dossier\n" +
              "# commentaire"
            }
            style={{
              width: "100%",
              minHeight: "100px",
              background: "#1a1a1a",
              color: "#fff",
              border: "1px solid #444",
              borderRadius: "4px",
              padding: "8px",
              fontFamily: "monospace",
              fontSize: "12px",
            }}
          />
        </PanelSectionRow>
        <PanelSectionRow>
          <ButtonItem
            layout="below"
            onClick={handleSaveAndCheck}
            disabled={busy !== null}
          >
            {busy === "check" ? "Vérification..." : "Sauvegarder & vérifier"}
          </ButtonItem>
        </PanelSectionRow>
      </PanelSection>

      <PanelSection title="État des plugins">
        {statuses.length === 0 && (
          <PanelSectionRow>Aucune vérification effectuée.</PanelSectionRow>
        )}
        {statuses.map((s) => (
          <PanelSectionRow key={s.repo}>
            <div style={{ width: "100%", padding: "4px 0" }}>
              <div style={{ fontWeight: "bold" }}>{s.name}</div>
              <div style={{ fontSize: "12px", opacity: 0.8 }}>
                Local : {s.local ?? "non installé"} — Distant : {s.remote ?? "?"}
              </div>
              {s.error && (
                <div style={{ color: "salmon", fontSize: "12px" }}>{s.error}</div>
              )}
              {s.update_available && !s.error && (
                <div style={{ marginTop: "6px" }}>
                  <ButtonItem
                    layout="below"
                    onClick={() => handleInstall(s)}
                    disabled={busy !== null}
                  >
                    {busy === s.name
                      ? "Installation..."
                      : `Mettre à jour → ${s.remote}`}
                  </ButtonItem>
                </div>
              )}
            </div>
          </PanelSectionRow>
        ))}
      </PanelSection>
    </>
  );
}

export default definePlugin(() => ({
  name: "Git Updater",
  titleView: <div className={staticClasses.Title}>Git Updater</div>,
  content: <Content />,
  icon: <FaGithub />,
  onDismount() {},
}));
