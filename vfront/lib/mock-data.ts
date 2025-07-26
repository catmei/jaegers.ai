export const mockData = {
  title: "爆紅短影音劇本：徐巧芯的輿論戰場 (60秒)",
  goal: "在60秒內呈現徐巧芯在兩岸議題上的複雜定位，以及中共如何利用台灣聲音進行宣傳。",
  style: ["懸疑", "緊湊", "資訊量大"],
  segments: [
    {
      time_range: "0:00-0:03",
      title: "開場：輿論漩渦",
      visual: [
        {
          sub_time_range: "0:00-0:03",
          type: "concept",
          source: null,
          description:
            "快速蒙太奇 徐巧芯的特寫、模糊的 中共黨徽和中國地圖 閃現。背景可加入新聞跑馬燈、社群媒體介面，營造資訊爆炸感。",
        },
      ],
      audio: "警報聲或心跳聲，逐漸增強的懸疑配樂。",
    },
    {
      time_range: "0:03-0:10",
      title: "來自中共媒體的聲音",
      visual: [
        {
          sub_time_range: "0:03-0:10",
          type: "concept",
          source: null,
          description:
            "快速剪輯 中共官媒（如台海網、海峽導報、中國台灣網）頭條，突出「徐巧芯」字樣與媒體Logo。穿插模糊的中共宣傳海報。",
        },
      ],
      audio: "電視新聞播報背景音，配樂轉為沉重。",
    },
    {
      time_range: "0:10-0:20",
      title: "中共的「以台批台」戰略",
      visual: [
        {
          sub_time_range: "0:10-0:20",
          type: "concept",
          source: null,
          description:
            "動畫圖表展示中共宣傳主題：戰爭威脅 (51%)、質疑美國 (24%)、兩岸一家親 (13%)。圖表快速跳轉，每個主題出現時有不同的代表性畫面。",
        },
      ],
      audio: "配樂節奏加快，加入短促的音效。",
    },
    {
      time_range: "0:20-0:35",
      title: "徐巧芯的言論 vs. 中共的放大鏡",
      visual: [
        {
          sub_time_range: "0:20-0:25",
          type: "concept",
          source: null,
          description:
            "展現徐巧芯批評民進黨的片段（找具代表性的，例如質疑政策、弊案等）。畫面一側是徐巧芯說話，另一側則快速閃過中共官媒對類似言論的報導截圖。",
        },
        {
          sub_time_range: "0:25-0:30",
          type: "clip",
          source: {
            platform: "youtube",
            url: "https://www.youtube.com/watch?v=G8MCrOg0j4o",
            time_range: "00:15:56 - 00:16:00",
          },
          description: "徐巧芯否認罷免方指控她是親共的說法，認為這是在抹黑抹紅。(剪輯此段最精華部分，表情堅定)。",
        },
        {
          sub_time_range: "0:30-0:35",
          type: "clip",
          source: {
            platform: "youtube",
            url: "https://www.youtube.com/watch?v=G8MCrOg0j4o",
            time_range: "00:16:14 - 00:16:36",
          },
          description:
            "徐巧芯重申她從政以來堅定反對中華人民共和國對中華民國的侵略，無論是武力還是認知作戰，都反對到底。(剪輯此段最具力量感的部分)。",
        },
      ],
      audio: "配樂轉為對話背景音，然後再切回緊湊配樂。",
    },
    {
      time_range: "0:35-0:45",
      title: "否認與質疑：言論的雙面刃",
      visual: [
        {
          sub_time_range: "0:35-0:40",
          type: "clip",
          source: {
            platform: "youtube",
            url: "https://www.youtube.com/watch?v=G8MCrOg0j4o",
            time_range: "00:17:07 - 00:17:11",
          },
          description:
            "徐巧芯反駁曹興誠指控她是中共地下黨員和掩護共諜的說法，反問如果她是，為何會揭露那麼多與中共相關的不法事件。(剪輯此段，展現徐巧芯的反駁)。",
        },
        {
          sub_time_range: "0:40-0:45",
          type: "clip",
          source: {
            platform: "youtube",
            url: "https://www.youtube.com/watch?v=G8MCrOg0j4o",
            time_range: "00:18:09 - 00:18:12",
          },
          description: "徐巧芯指控曹興誠才是最親中投共的始祖。(剪輯此段，製造戲劇性衝突)。",
        },
      ],
      audio: "辯論式的配樂，或短促的爭議音效。",
    },
    {
      time_range: "0:45-0:55",
      title: "誰是受害者？誰是推手？",
      visual: [
        {
          sub_time_range: "0:45-0:55",
          type: "concept",
          source: null,
          description:
            "快速閃現中共官媒將徐巧芯言論「斷章取義」或「刻意放大」的對比畫面（若有此類素材更佳，否則可用文字疭加說明）。",
        },
      ],
      audio: "懸疑音樂達到高潮，然後漸弱。",
    },
    {
      time_range: "0:55-1:00",
      title: "結尾：思考與警惕",
      visual: [
        {
          sub_time_range: "0:55-1:00",
          type: "concept",
          source: null,
          description: "畫面逐漸定格在一個問號，或中共黨徽與台灣地圖的模糊重疊。",
        },
      ],
      audio: "懸疑音樂結束，留下一個沉重的尾音。",
    },
  ],
}
