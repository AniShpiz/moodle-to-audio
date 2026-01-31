// ==UserScript==
// @name         Moodle Video Master - Extractor
// @namespace    http://tampermonkey.net/
// @version      1.1
// @description  Extract direct MP4 links from Moodle video tables for MP3 conversion
// @author       You
// @match        *://*/*moodle*
// @grant        GM_setClipboard
// ==/UserScript==

(function () {
    'use strict';

    // Create UI Button
    const btn = document.createElement('button');
    btn.innerHTML = '🚀 Extract Links for MP3';
    btn.style = 'position:fixed;top:20px;right:20px;z-index:9999;padding:12px;background:#ff4444;color:white;border:none;border-radius:8px;font-weight:bold;cursor:pointer;box-shadow:0 4px 6px rgba(0,0,0,0.2);';
    document.body.appendChild(btn);

    // Progress indicator
    const progress = document.createElement('div');
    progress.style = 'position:fixed;top:70px;right:20px;z-index:9999;padding:8px 12px;background:#333;color:white;border-radius:6px;font-size:12px;display:none;';
    document.body.appendChild(progress);

    btn.onclick = async () => {
        // Step 1: Get all links from the video table
        const tableBody = document.querySelector("#videoslist_table > tbody");
        if (!tableBody) {
            alert("טבלת הסרטונים לא נמצאה! (#videoslist_table > tbody)");
            return;
        }

        const allLinks = Array.from(tableBody.querySelectorAll("a"));

        // Filter to video/php links (sub-pages containing videos)
        const subPageUrls = allLinks
            .map(a => a.href)
            .filter(href => href.includes("php") || href.includes("video"));

        if (subPageUrls.length === 0) {
            alert("לא נמצאו קישורים לסרטונים בטבלה!");
            return;
        }

        btn.innerHTML = 'מחלץ... ⏳';
        btn.disabled = true;
        progress.style.display = 'block';

        let directVideoLinks = [];
        let processed = 0;

        // Step 2: Fetch each sub-page and extract the actual video URL
        for (const pageUrl of subPageUrls) {
            try {
                progress.textContent = `מעבד ${++processed}/${subPageUrls.length}...`;

                const response = await fetch(pageUrl);
                const html = await response.text();

                // Try multiple patterns to find the video URL
                let videoUrl = null;

                // Pattern 1: Cloudfront MP4
                const cloudfrontMatch = html.match(/https:\/\/[a-z0-9]+\.cloudfront\.net\/[^"'\s]+\.mp4/i);
                if (cloudfrontMatch) videoUrl = cloudfrontMatch[0];

                // Pattern 2: Any MP4 source in video tag
                if (!videoUrl) {
                    const mp4Match = html.match(/src=["']([^"']+\.mp4)[^"']*/i);
                    if (mp4Match) videoUrl = mp4Match[1];
                }

                // Pattern 3: Generic video URL pattern
                if (!videoUrl) {
                    const genericMatch = html.match(/https?:\/\/[^"'\s]+\.mp4/i);
                    if (genericMatch) videoUrl = genericMatch[0];
                }

                if (videoUrl) {
                    directVideoLinks.push(videoUrl);
                    console.log(`✅ Found: ${videoUrl}`);
                } else {
                    console.warn(`❌ No video found in: ${pageUrl}`);
                }

            } catch (e) {
                console.error(`Error fetching: ${pageUrl}`, e);
            }
        }

        // Remove duplicates
        directVideoLinks = [...new Set(directVideoLinks)];

        // Copy to clipboard
        GM_setClipboard(directVideoLinks.join('\n'));

        btn.innerHTML = '✅ הועתק!';
        btn.disabled = false;
        progress.style.display = 'none';

        alert(`חולצו ${directVideoLinks.length} קישורים ישירים לסרטונים!\nהרשימה הועתקה ללוח.\n\nהדבק אותם ב-links.txt והרץ את הסקריפט.`);

        console.log("=== Direct Video Links ===");
        console.log(directVideoLinks.join('\n'));

        // Reset button after 3 seconds
        setTimeout(() => { btn.innerHTML = '🚀 Extract Links for MP3'; }, 3000);
    };
})();
