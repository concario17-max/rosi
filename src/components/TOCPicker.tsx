import { CSSProperties, useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { ChevronDown, ChevronLeft, ChevronRight, Flower, X } from 'lucide-react';
import { YogaChapter } from '../types';
import { getPreviousSutraTarget, getNextSutraTarget } from '../utils/sutraNavigation';

interface TOCPickerProps {
    chapterNum?: string;
    verseNum?: string;
    chapters: YogaChapter[];
    allChapters: Record<number, YogaChapter> | null;
    onCommitSelection: (chapter: string, verse: string) => void;
}

export const TOCPicker = ({
    chapterNum,
    verseNum,
    chapters,
    allChapters,
    onCommitSelection,
}: TOCPickerProps) => {
    const [isOpen, setIsOpen] = useState(false);
    const [expandedChapter, setExpandedChapter] = useState<number | null>(null);
    
    const rootRef = useRef<HTMLDivElement>(null);
    const triggerRef = useRef<HTMLButtonElement>(null);
    const panelRef = useRef<HTMLDivElement>(null);
    const [panelStyle, setPanelStyle] = useState<CSSProperties | null>(null);

    // active 챕터 및 절 구하기
    const activeChapter = useMemo(() => {
        return chapters.find((c) => String(c.chapter) === chapterNum);
    }, [chapters, chapterNum]);

    // 초기 로드 또는 현재 챕터 변경 시 탭 및 챕터 기본값 설정
    useEffect(() => {
        if (activeChapter) {
            setExpandedChapter(activeChapter.chapter);
        }
    }, [activeChapter]);

    // 패널 닫기 이벤트 핸들러
    useEffect(() => {
        if (!isOpen) return;

        const handlePointerDown = (event: PointerEvent) => {
            const target = event.target as Node;
            if (
                rootRef.current &&
                !rootRef.current.contains(target) &&
                !panelRef.current?.contains(target)
            ) {
                setIsOpen(false);
            }
        };

        const handleKeyDown = (event: KeyboardEvent) => {
            if (event.key === 'Escape') {
                setIsOpen(false);
            }
        };

        document.addEventListener('pointerdown', handlePointerDown);
        document.addEventListener('keydown', handleKeyDown);

        return () => {
            document.removeEventListener('pointerdown', handlePointerDown);
            document.removeEventListener('keydown', handleKeyDown);
        };
    }, [isOpen]);

    // 패널 위치 계산
    useLayoutEffect(() => {
        if (!isOpen || !triggerRef.current) return;

        const updatePosition = () => {
            const rect = triggerRef.current?.getBoundingClientRect();
            if (!rect) return;

            const panelWidth = Math.min(500, window.innerWidth - 24);
            const left = Math.min(Math.max(rect.left, 12), window.innerWidth - panelWidth - 12);
            const top = rect.bottom + 8;

            setPanelStyle({
                position: 'fixed',
                top: `${Math.round(top)}px`,
                left: `${Math.round(left)}px`,
                width: `${Math.round(panelWidth)}px`,
            });
        };

        updatePosition();
        window.addEventListener('resize', updatePosition);
        window.addEventListener('scroll', updatePosition, true);

        return () => {
            window.removeEventListener('resize', updatePosition);
            window.removeEventListener('scroll', updatePosition, true);
        };
    }, [isOpen]);

    // 트리거 텍스트 계산
    const triggerText = useMemo(() => {
        if (!activeChapter) return '목차 선택';
        const formattedVerseNum = verseNum && !isNaN(Number(verseNum)) ? `${verseNum}문단` : (verseNum || '');
        return formattedVerseNum ? `${activeChapter.chapter}강. ${activeChapter.meta.name_korean} / ${formattedVerseNum}` : `${activeChapter.chapter}강. ${activeChapter.meta.name_korean}`;
    }, [activeChapter, verseNum]);

    // 이전/다음 절 이동 타겟 구하기
    const activeVerseIndex = useMemo(() => {
        if (!activeChapter) return -1;
        return activeChapter.sutras.findIndex(
            (s) => String(s.verse ?? Number.parseInt(s.id.split('.')[1], 10)) === verseNum
        );
    }, [activeChapter, verseNum]);

    const prevTarget = useMemo(() => {
        return getPreviousSutraTarget(allChapters, chapterNum, activeVerseIndex);
    }, [allChapters, chapterNum, activeVerseIndex]);

    const nextTarget = useMemo(() => {
        return getNextSutraTarget(allChapters, chapterNum, activeVerseIndex);
    }, [allChapters, chapterNum, activeVerseIndex]);

    const totalVerses = activeChapter?.sutras.length || 0;

    const expandedChapterData = useMemo(() => {
        return chapters.find((c) => c.chapter === expandedChapter) || null;
    }, [chapters, expandedChapter]);

    const panel = isOpen ? (
        <div
            role="dialog"
            aria-label="TOC Picker"
            ref={panelRef}
            style={panelStyle ?? undefined}
            className="z-[60] flex flex-col max-h-[460px] rounded-[1.75rem] border border-gold-border/12 bg-[linear-gradient(180deg,rgba(255,251,241,0.98)_0%,rgba(252,247,237,0.96)_48%,rgba(245,238,228,0.92)_100%)] p-4 shadow-[0_26px_72px_-34px_rgba(0,0,0,0.58)] backdrop-blur-2xl dark:border-dark-border/70 dark:bg-[linear-gradient(180deg,rgba(24,20,15,0.98)_0%,rgba(20,17,13,0.96)_48%,rgba(15,13,10,0.92)_100%)] select-none overflow-hidden"
        >
            {/* Header */}
            <div className="flex items-center justify-between border-b border-gold-border/8 pb-3 mb-3 dark:border-dark-border/30 shrink-0">
                <div className="flex items-center gap-3">
                    <span className="inline-flex items-center gap-1 rounded-full bg-gold-primary/10 px-2.5 py-0.5 text-[9px] font-bold uppercase tracking-[0.18em] text-gold-primary dark:bg-gold-light/10 dark:text-gold-light">
                        <Flower className="h-2.5 w-2.5" />
                        강연 탐색기
                    </span>
                    <span className="text-[10px] font-semibold tracking-[0.06em] text-text-secondary/75 dark:text-dark-text-secondary/70">
                        제 {chapterNum}강 / {verseNum}문단
                    </span>
                </div>
                <button
                    type="button"
                    onClick={() => setIsOpen(false)}
                    className="rounded-full p-1.5 hover:bg-gold-primary/8 dark:hover:bg-gold-light/8 text-text-secondary/60 dark:text-dark-text-secondary/50 transition-colors cursor-pointer"
                >
                    <X className="h-3.5 w-3.5" />
                </button>
            </div>

            {/* 2-Column Split Content Area */}
            <div className="flex flex-1 min-h-0 divide-x divide-gold-border/8 dark:divide-dark-border/30 overflow-hidden">
                {/* Left Column: Chapters (Lectures) */}
                <div className="w-[125px] sm:w-[155px] shrink-0 overflow-y-auto pr-3.5 space-y-1.5 custom-scrollbar">
                    <p className="text-[9px] font-bold uppercase tracking-[0.15em] text-gold-primary/60 dark:text-gold-light/60 mb-2 px-1">
                        강연 목록
                    </p>
                    {chapters.map((ch) => {
                        const isActive = expandedChapter === ch.chapter;
                        return (
                            <button
                                key={ch.chapter}
                                type="button"
                                onClick={() => setExpandedChapter(ch.chapter)}
                                className={`w-full text-left px-3 py-2.5 rounded-xl text-[11px] font-bold tracking-[0.02em] transition-all duration-200 cursor-pointer ${
                                    isActive
                                        ? 'bg-gold-primary text-white dark:bg-gold-light dark:text-[#2a2116] shadow-sm'
                                        : 'text-text-primary hover:bg-gold-primary/5 dark:text-dark-text-primary dark:hover:bg-gold-light/5'
                                }`}
                            >
                                {ch.chapter}강. {ch.meta.name_korean}
                            </button>
                        );
                    })}
                </div>

                {/* Right Column: Paragraphs */}
                <div className="flex-1 overflow-y-auto pl-3.5 custom-scrollbar">
                    <p className="text-[9px] font-bold uppercase tracking-[0.15em] text-gold-primary/60 dark:text-gold-light/60 mb-2 px-1">
                        문단 선택
                    </p>
                    {expandedChapterData ? (
                        <div className="grid grid-cols-4 sm:grid-cols-5 gap-2 pr-1 pb-1">
                            {expandedChapterData.sutras.map((sutra) => {
                                const vNum = String(sutra.verse ?? Number.parseInt(sutra.id.split('.')[1], 10));
                                const isCurrent = String(expandedChapterData.chapter) === chapterNum && String(vNum) === verseNum;
                                return (
                                    <button
                                        key={sutra.id}
                                        type="button"
                                        onClick={() => {
                                            onCommitSelection(String(expandedChapterData.chapter), vNum);
                                            setIsOpen(false);
                                        }}
                                        className={`h-9 rounded-xl flex items-center justify-center text-[11px] font-bold border transition-all duration-200 cursor-pointer ${
                                            isCurrent
                                                ? 'bg-gold-primary/10 border-gold-primary text-gold-primary dark:bg-gold-light/10 dark:border-gold-light dark:text-gold-light shadow-[0_2px_8px_-2px_rgba(166,139,92,0.25)] font-extrabold'
                                                : 'bg-white/40 border-gold-border/8 text-text-primary hover:border-gold-border/20 hover:bg-white/90 dark:bg-white/3 dark:border-dark-border/40 dark:text-dark-text-primary dark:hover:bg-white/6'
                                        }`}
                                    >
                                        {vNum}
                                    </button>
                                );
                            })}
                        </div>
                    ) : (
                        <div className="text-center py-12 text-[11px] text-text-secondary/50 dark:text-dark-text-secondary/50">
                            강연을 선택해 주세요.
                        </div>
                    )}
                </div>
            </div>

            {/* Stepper Footer */}
            <div className="mt-3 border-t border-gold-border/12 pt-3 dark:border-dark-border/55 flex items-center justify-between shrink-0">
                <button
                    type="button"
                    disabled={!prevTarget}
                    onClick={() => {
                        if (prevTarget) {
                            onCommitSelection(String(prevTarget.chapter), prevTarget.verse);
                        }
                    }}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-gold-border/15 dark:border-dark-border/50 text-[10px] font-semibold text-text-primary dark:text-dark-text-primary hover:bg-gold-primary/5 dark:hover:bg-gold-light/5 disabled:opacity-40 disabled:pointer-events-none transition-colors cursor-pointer"
                >
                    <ChevronLeft className="h-3.5 w-3.5" />
                    이전 문단
                </button>

                <div className="flex items-center gap-1 text-[11px] font-bold text-gold-primary dark:text-gold-light">
                    <span>{verseNum}</span>
                    <span className="text-text-secondary/50 dark:text-dark-text-secondary/50 font-normal">/</span>
                    <span className="text-text-secondary/80 dark:text-dark-text-secondary/80 font-normal">{totalVerses}</span>
                </div>

                <button
                    type="button"
                    disabled={!nextTarget}
                    onClick={() => {
                        if (nextTarget) {
                            onCommitSelection(String(nextTarget.chapter), nextTarget.verse);
                        }
                    }}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-gold-border/15 dark:border-dark-border/50 text-[10px] font-semibold text-text-primary dark:text-dark-text-primary hover:bg-gold-primary/5 dark:hover:bg-gold-light/5 disabled:opacity-40 disabled:pointer-events-none transition-colors cursor-pointer"
                >
                    다음 문단
                    <ChevronRight className="h-3.5 w-3.5" />
                </button>
            </div>
        </div>
    ) : null;

    return (
        <div ref={rootRef} className="relative shrink-0">
            <button
                ref={triggerRef}
                type="button"
                onClick={() => setIsOpen((prev) => !prev)}
                aria-expanded={isOpen}
                aria-haspopup="dialog"
                className="inline-flex items-center rounded-full border border-gold-border/14 bg-shell-main/82 p-0.5 shadow-[0_10px_28px_-22px_rgba(0,0,0,0.32)] backdrop-blur-sm transition-all duration-300 hover:-translate-y-0.5 hover:border-gold-border/24 hover:bg-shell-main/92 active:translate-y-0 dark:border-dark-border/70 dark:bg-shell-main-dark/82 dark:hover:bg-shell-main-dark/88 cursor-pointer"
            >
                <span className="inline-flex items-center gap-2.5 rounded-full bg-transparent px-4 py-1.5 text-[11px] font-semibold tracking-[0.02em] text-gold-primary dark:text-gold-light">
                    <span className="max-w-[170px] sm:max-w-[280px] md:max-w-[340px] truncate whitespace-nowrap">{triggerText}</span>
                    <ChevronDown className={`h-3.5 w-3.5 shrink-0 transition-transform duration-300 ${isOpen ? 'rotate-180' : ''}`} />
                </span>
            </button>

            {isOpen ? createPortal(panel, document.body) : null}
        </div>
    );
};
