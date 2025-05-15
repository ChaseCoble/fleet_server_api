// ==UserScript==
// @name         Arxiv Scraper and Explainer (Chunked)
// @namespace    http://tampermonkey.net/
// @version      2025-05-12
// @description  Scrapes article content, chunks at sentence boundaries, sends to local API for explanation, and inserts responses.
// @author       You
// @match        https://arxiv.org/html/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=arxiv.org
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    const API_ENDPOINT = 'https://127.0.0.1:8000/v1/request';
    const LONG_CONTENT_THRESHOLD = 1000;
    const ROOT_TEST_ENDPOINT = `http://localhost:8000/`;
    const QUICK_TEST = true;

    window.addEventListener('load', () => {
        console.log("Arxiv Scraper script loaded.");
        const willScrape = confirm("Do you want to scrape this article and get explanations?");
        if (willScrape) {
            console.log("Scraping article...");
            scrapeAndProcessArticle();
        } else {
            console.log("Article scraping skipped by user.");
        }
    });

    async function scrapeAndProcessArticle() {
        const scrapedData = scrapeArticleData();

        if (!scrapedData) {
            console.error("Failed to scrape article data.");
            return;
        }

        console.log("Scraped Data:", scrapedData);

        try {
            const requestPayload = buildRequestPayload(scrapedData);
            console.log("Request Payload:", JSON.stringify(requestPayload, null, 2));

            console.log(`Sending data to API at ${API_ENDPOINT}...`);
            const response = await fetch(API_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestPayload)
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
            }

            const responseData = await response.json();
            console.log("API Response:", responseData);

            insertResponsesIntoDom(responseData, scrapedData.fusedElements, scrapedData.paragraphElementsMap);

        } catch (error) {
            console.error("Error processing article or communicating with API:", error);
            alert("An error occurred while processing the article. Check the browser console for details.");
        }
    }

    function scrapeArticleData() {
        try {
            const url = window.location.href;
            const access_date = new Date().toISOString();
            const title = extract_title();
            const authors = extract_authors();
            const publish_date = extract_publish_date();
            const paragraphElements = Array.from(document.getElementsByClassName('ltx_p'));
            const paragraphsText = paragraphElements.map(p => Array.from(p.childNodes)
                .filter(node => node.nodeType === Node.TEXT_NODE || node.nodeType === Node.ELEMENT_NODE)
                .map(node => node.nodeType === Node.TEXT_NODE ? node.textContent : node.outerHTML)
                .join('')
                .trim()
            ).filter(text => text.length > 0);

            // Fuse paragraphs and elements together with sentence boundary logic
            const { fusedParagraphs, fusedElements } = fuseParagraphsAndElementsBySentence(paragraphsText, paragraphElements);

            // Data Tests (optional, keep for debugging)
            console.log(`Title: ${title}`);
            console.log(`Authors: ${authors}`);
            console.log(`Found ${paragraphElements.length} potential paragraphs, ${fusedParagraphs.length} fused chunks.`);
            console.log(`URL: ${url}`);
            console.log(`Access Date: ${access_date}`);
            console.log(`Publish Date: ${publish_date}`);

            if (fusedParagraphs.length === 0) {
                console.warn("No paragraphs found to process.");
                return null; // Indicate failure
            }

            return {
                title: title,
                authors: authors,
                url: url,
                publish_date: publish_date,
                access_date: access_date,
                fusedParagraphs: fusedParagraphs,
                fusedElements: fusedElements,
                paragraphElements: paragraphElements // For reference, may not be needed
            };
        } catch (error) {
            console.error("Error during scraping:", error);
            return null; // Indicate failure
        }
    }

    function buildRequestPayload(scrapedData) {
        const context_arr = scrapedData.fusedParagraphs.unshift("You are an expert teacher in this subject.\n\n");

        const requestId = crypto.randomUUID();
        const contextItemId = crypto.randomUUID();
        const contentItems = [];
        const paragraphElementsMap = new Map();
        const contextItems = [];

        scrapedData.fusedParagraphs.forEach((paragraphText, index) => {
            const originalParagraphElements = scrapedData.fusedElements[index];
            if (!originalParagraphElements || originalParagraphElements.length === 0) {
                console.warn(`Could not find DOM elements for chunk index ${index}. Skipping.`);
                return;
            }

            const paragraphItemId = crypto.randomUUID();
            contextItems.push({
                prompt_item_id: contextItemId,
                item: paragraphText,
                is_long: paragraphText.length > LONG_CONTENT_THRESHOLD
            });

            contentItems.push({
                prompt_item_id: paragraphItemId,
                item: "Explain this to me clearly and expansively as possible.\n\n" + paragraphText,
                is_long: paragraphText.length > LONG_CONTENT_THRESHOLD
            });

            // Map the item ID to the LAST element in the chunk for insertion
            paragraphElementsMap.set(paragraphItemId, originalParagraphElements[originalParagraphElements.length - 1]);
        });

        contextItems.unshift({
            prompt_item_id: contextItemId,
            item: "You are an expert in teaching this field to any experience level",
            is_long: false
        });

        scrapedData.paragraphElementsMap = paragraphElementsMap;

        const test_request_payload = {
            id: requestId,
            no_cache: false,
            no_store: false,
            timestamp: scrapedData.access_date,
            context: contextItems.slice(0,28),
            content: contentItems.slice(0, 5)
        };
        const requestPayload = {
            id: requestId,
            no_cache: false,
            no_store: false,
            timestamp: scrapedData.access_date,
            context: contextItems,
            content: contentItems
        };
        if (QUICK_TEST) {
            return test_request_payload;
        }
        return requestPayload;
    }

    function insertResponsesIntoDom(responseData, fusedElements, paragraphElementsMap) {
        if (!responseData || !responseData.responses || responseData.responses.length === 0) {
            console.warn("No responses received from the API.");
            return;
        }

        console.log(`Inserting ${responseData.responses.length} responses into the DOM.`);

        responseData.responses.forEach(responseItem => {
            const promptItemId = responseItem.id;
            const responseText = responseItem.prompt_response;

            if (!promptItemId || !responseText) {
                console.warn(`Skipping response item due to missing ID or response text:`, responseItem);
                return;
            }

            const targetParagraphElement = paragraphElementsMap.get(promptItemId);

            if (targetParagraphElement) {
                const responseDiv = document.createElement('div');
                responseDiv.classList.add('arxiv-explainer-response');
                responseDiv.style.border = '1px solid #ccc';
                responseDiv.style.padding = '10px';
                responseDiv.style.margin = '10px 0';
                responseDiv.style.backgroundColor = '#f9f9f9';
                responseDiv.style.whiteSpace = 'pre-wrap';
                responseDiv.textContent = responseText;
                targetParagraphElement.after(responseDiv);
                console.log(`Inserted response for item ID: ${promptItemId}`);
            } else {
                console.warn(`Could not find target paragraph element for item ID: ${promptItemId}`);
            }
        });
    }

    // --- Helper Functions ---

    function extract_title() {
        const titleElement = document.querySelector('h1.ltx_title.ltx_title_document');
        return titleElement ? titleElement.textContent.trim() : "Untitled";
    }

    function extract_publish_date() {
        let publish_date = null;
        try {
            const watermarkElement = document.querySelector("#watermark-tr");
            if (watermarkElement) {
                const text = watermarkElement.textContent;
                const publish_date_regex = /(\d{1,2} \w{3} \d{4})/;
                const match = text.match(publish_date_regex);
                if (match) {
                    const dateString = match[1];
                    const date = new Date(dateString);
                    if (!isNaN(date.getTime())) {
                        publish_date = date.toISOString();
                    } else {
                        console.warn(`Failed to parse date string: ${dateString}`);
                    }
                } else {
                    console.warn("Publish date regex did not match in watermark text.");
                }
            } else {
                console.warn("Could not find #watermark-tr element.");
            }
        } catch (e) {
            console.error("Error extracting publish date:", e);
        }
        return publish_date;
    }

    function extract_authors() {
        const authors = document.getElementsByClassName('ltx_role_author');
        const personNames = [];
        for (let i = 0; i < authors.length; i++) {
            const personNameElement = authors[i].querySelector('.ltx_personname');
            if (personNameElement) {
                personNames.push(personNameElement.textContent.trim());
            }
        }
        return personNames;
    }

    /**
     * Fuses small paragraphs/one-liners into larger chunks, ending at sentence boundaries if possible.
     * @param {string[]} paragraphs - Array of paragraph strings.
     * @param {Element[]} elements - Array of corresponding DOM elements.
     * @param {number} minLength - Minimum length of a chunk in characters.
     * @returns {{ fusedParagraphs: string[], fusedElements: Element[][] }}
     */
    function fuseParagraphsAndElementsBySentence(paragraphs, elements, minLength = 2000) {
        const fusedParagraphs = [];
        const fusedElements = [];
        let buffer = "";
        let bufferElements = [];
        const sentenceEndRegex = /[.!?](?=\s|$)/g;

        for (let i = 0; i < paragraphs.length; i++) {
            const para = paragraphs[i].trim();
            if (!para) continue;

            if (!buffer) {
                buffer = para;
                bufferElements = [elements[i]];
            } else {
                buffer += " " + para;
                bufferElements.push(elements[i]);
            }

            // If buffer is long enough, try to end at a sentence boundary
            if (buffer.length >= minLength) {
                // Find the last sentence-ending punctuation in the buffer
                let lastMatch = -1;
                let match;
                while ((match = sentenceEndRegex.exec(buffer)) !== null) {
                    lastMatch = match.index + match[0].length;
                }
                if (lastMatch !== -1 && lastMatch > minLength * 0.5) {
                    // Split at the last sentence end
                    fusedParagraphs.push(buffer.slice(0, lastMatch).trim());
                    fusedElements.push(bufferElements.slice());
                    // Start new buffer with the remaining text
                    buffer = buffer.slice(lastMatch).trim();
                    bufferElements = buffer ? [elements[i]] : [];
                }
            }
        }
        if (buffer) {
            fusedParagraphs.push(buffer);
            fusedElements.push(bufferElements);
        }
        return { fusedParagraphs, fusedElements };
    }

})();
