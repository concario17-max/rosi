import { YogaChapter, YogaSutra } from '../types';

let cachedData: Record<number, YogaChapter> | null = null;
let pendingRequest: Promise<Record<number, YogaChapter>> | null = null;

const stripBom = (value: string) => (value.charCodeAt(0) === 0xfeff ? value.slice(1) : value);

type ReadingDataText = {
    german?: string;
    english?: string;
    korean?: string;
    ai_translation?: string;
};

type ReadingDataParagraph = {
    id: string;
    title?: string;
    paragraphNumber?: number;
    chapterTitle?: string;
    text?: ReadingDataText;
};

type ReadingDataSubchapter = {
    id: string;
    chapterName?: string;
    title?: string;
    tocHeadings?: string[];
    tocActionLabel?: string;
    paragraphs?: ReadingDataParagraph[];
};

type ReadingDataGroup = {
    id: string;
    chapterName?: string;
    title?: string;
    isGroup?: boolean;
    subchapters?: ReadingDataSubchapter[];
    paragraphs?: ReadingDataParagraph[];
};

type ReadingDataSnapshot = {
    chapters?: ReadingDataGroup[];
    flatParagraphs?: ReadingDataParagraph[];
};

const normalizeParagraph = (
    chapterNum: number,
    paragraph: ReadingDataParagraph,
    paragraphIndex: number,
): YogaSutra => {
    const sourceText = paragraph.text ?? { german: '', english: '', korean: '', ai_translation: '' };
    const verseNumber = typeof paragraph.paragraphNumber === 'number' ? paragraph.paragraphNumber : paragraphIndex + 1;

    return {
        id: paragraph.id || `${chapterNum}.${verseNumber}`,
        chapter: chapterNum,
        verse: verseNumber,
        title: paragraph.title || undefined,
        german: sourceText.german || '',
        english: sourceText.english || '',
        korean: sourceText.korean || '',
        ai_translation: sourceText.ai_translation || '',
        pronunciation: '',
        pronunciation_kr: '',
        sanskrit: '',
        // Provide legacy properties so other components don't crash before refactoring
        translation_en: sourceText.english || '',
        translation_ham: sourceText.korean || '',
    };
};

const normalizeSubchapter = (
    chapterNum: number,
    groupTitle: string,
    groupName: string,
    subchapter: ReadingDataSubchapter,
): YogaChapter => {
    const sutras = (subchapter.paragraphs ?? []).map((paragraph, index) => {
        return normalizeParagraph(chapterNum, paragraph, index);
    });

    return {
        chapter: chapterNum,
        meta: {
            chapter: chapterNum,
            name_korean: subchapter.chapterName || groupName || `Chapter ${chapterNum}`,
            name_english: subchapter.title || subchapter.chapterName || groupTitle || `Chapter ${chapterNum}`,
            description: groupTitle || subchapter.chapterName || '',
            sutraCount: sutras.length,
        },
        sutras,
    };
};

const flattenSubchapters = (snapshot: ReadingDataSnapshot) =>
    (snapshot.chapters ?? [])
        .filter((group) => group.id === 'bodhi')
        .flatMap((group) =>
            (group.subchapters ?? []).map((subchapter) => ({
                group,
                subchapter,
            })),
        );

export const resetCache = () => {
    cachedData = null;
    pendingRequest = null;
};

export const fetchYogaData = async (): Promise<Record<number, YogaChapter>> => {
    if (cachedData) {
        return cachedData;
    }

    if (pendingRequest) {
        return pendingRequest;
    }

    pendingRequest = (async () => {
        try {
            const dataRes = await fetch('/reading-data.json');

            if (!dataRes.ok) {
                throw new Error(`Failed to fetch reading data: ${dataRes.status}`);
            }

            const snapshot = JSON.parse(stripBom(await dataRes.text())) as ReadingDataSnapshot;
            
            const structuredData = flattenSubchapters(snapshot).reduce<Record<number, YogaChapter>>((acc, entry, index) => {
                const chapterNumber = index + 1;
                acc[chapterNumber] = normalizeSubchapter(
                    chapterNumber,
                    entry.group.title || entry.group.chapterName || '',
                    entry.group.chapterName || entry.group.title || '',
                    entry.subchapter,
                );
                return acc;
            }, {});

            cachedData = structuredData;
            return structuredData;
        } catch (error) {
            console.error('Error fetching reading data:', error);
            throw error instanceof Error ? error : new Error('Unknown reading data fetch failure');
        } finally {
            pendingRequest = null;
        }
    })();

    return pendingRequest;
};
