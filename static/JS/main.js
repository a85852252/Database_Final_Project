// main.js
// 全站 JS 功能主入口，統一管理所有常用 JS 模組
// 依據頁面功能自動載入所需功能（模組化方便維護、分頁載入更輕量）

// 管理 flash 訊息彈窗淡出效果
import './function/flash.js';

// 支援首頁卡片搜尋/即時過濾
import './function/search.js';

// 支援「回到頂部」按鈕功能
import './function/backtotop.js';

// 商品圖片即時預覽（用於商品上架頁）
import './function/image_preview.js';

// 初始化 Choices.js 下拉多選美化（上架、搜尋頁使用）
import './function/choices_init.js';
