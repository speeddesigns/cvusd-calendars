import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { CalendarExplorer } from "./CalendarExplorer";
import "./styles.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <CalendarExplorer />
  </StrictMode>,
);
