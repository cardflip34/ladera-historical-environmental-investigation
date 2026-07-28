"use client";

import dynamic from "next/dynamic";
import type { AtlasProps } from "./AtlasView";

const AtlasView = dynamic(() => import("./AtlasView"), {
  ssr: false,
  loading: () => <p className="muted">Loading historical atlas...</p>,
});

export default function ClientAtlasView(props: AtlasProps) {
  return <AtlasView {...props} />;
}
