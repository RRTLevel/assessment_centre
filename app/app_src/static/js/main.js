

function readJson(id) {
    const el = document.getElementById(id);
    return el ? JSON.parse(el.textContent) : null;
}

function escHtml(s) {
    return String(s)
        .replace(/&/g, '&amp;').replace(/</g, '&lt;')
        .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function stripHtml(s) {
    return String(s).replace(/<[^>]+>/g, '').replace(/&nbsp;/g, ' ').trim();
}

const SUMMERNOTE_TOOLBAR = [
    ['style', ['bold', 'italic', 'underline']],
    ['color', ['forecolor']],
    ['para', ['ul', 'ol']],
    ['misc', ['undo', 'redo']],
];

function hasSummernote() {
    return window.jQuery && jQuery.fn.summernote;
}



const themeQuery = window.matchMedia('(prefers-color-scheme: dark)');

function activeThemeForPreference(preference) {
    if (preference === 'system') {
        return themeQuery.matches ? 'dark' : 'light';
    }
    return preference;
}

function applyThemePreference(preference) {
    localStorage.setItem('siteTheme', preference);
    document.documentElement.dataset.theme = activeThemeForPreference(preference);
    document.documentElement.dataset.themePreference = preference;
}

applyThemePreference(localStorage.getItem('siteTheme') || 'system');

themeQuery.addEventListener('change', () => {
    const preference = localStorage.getItem('siteTheme') || 'system';
    if (preference === 'system') {
        applyThemePreference(preference);
    }
});

/* Theme radio buttons on the profile page. */
document.addEventListener('DOMContentLoaded', () => {
    const radios = document.querySelectorAll('input[name="theme"]');
    if (!radios.length) return;

    const saved = localStorage.getItem('siteTheme') || 'system';
    radios.forEach((input) => {
        input.checked = input.value === saved;
        input.addEventListener('change', () => applyThemePreference(input.value));
    });
});

/* ────────────────────────── 3. Toast messages ────────────────────────── */

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-toast]').forEach((toast) => {
        const dismiss = () => {
            toast.classList.add('toast-hiding');
            window.setTimeout(() => toast.remove(), 250);
        };

        toast.querySelector('.toast-close')?.addEventListener('click', dismiss);
        window.setTimeout(dismiss, 4000);
    });
});

/* ────────────────────────── 4. Navbar burger ────────────────────────── */

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.navbar-burger').forEach((burger) => {
        burger.addEventListener('click', () => {
            const target = document.getElementById(burger.dataset.target);
            burger.classList.toggle('is-active');
            target?.classList.toggle('is-active');
        });
    });
});

/* ─────────────────── 5. Password visibility toggles ─────────────────── */
/* <span class="toggle-password" data-target="<input id>"><i class="toggle-icon fa-eye"></i></span> */

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.toggle-password').forEach((button) => {
        button.addEventListener('click', () => {
            const input = document.getElementById(button.getAttribute('data-target'));
            const icon = button.querySelector('.toggle-icon');
            if (!input) return;

            input.type = input.type === 'password' ? 'text' : 'password';
            icon?.classList.toggle('fa-eye');
            icon?.classList.toggle('fa-eye-slash');
        });
    });
});

/* ─────────────────── 6. Modals + confirm prompts ─────────────────── */
/* [data-open-modal="<id>"] opens a Bulma modal, [data-close-modal] closes the
   one it sits in, and clicking .modal-background closes too.
   [data-confirm="message"] asks before a click goes through. */

document.addEventListener('click', (event) => {
    const opener = event.target.closest('[data-open-modal]');
    if (opener) {
        document.getElementById(opener.getAttribute('data-open-modal'))?.classList.add('is-active');
        return;
    }

    const closer = event.target.closest('[data-close-modal]');
    if (closer) {
        closer.closest('.modal')?.classList.remove('is-active');
        return;
    }

    if (event.target.classList.contains('modal-background')) {
        event.target.closest('.modal')?.classList.remove('is-active');
    }

    const confirmed = event.target.closest('[data-confirm]');
    if (confirmed && !window.confirm(confirmed.getAttribute('data-confirm'))) {
        event.preventDefault();
    }
});

/* ─────────────────── 7. Summernote rich text editors ─────────────────── */
/* Any .richtext textarea becomes an editor; the hidden textarea is kept in
   sync so plain form submits carry the HTML. */

document.addEventListener('DOMContentLoaded', () => {
    if (!hasSummernote()) return;

    jQuery('.richtext').each(function () {
        jQuery(this).summernote({
            toolbar: SUMMERNOTE_TOOLBAR,
            height: 100,
            placeholder: this.getAttribute('data-placeholder') || '',
            callbacks: { onChange: function (contents) { jQuery(this).val(contents); } },
        });
    });
});

/* ─────────────────── 8. Create pack: question pickers ─────────────────── */
/* Selecting a category loads its bank questions into the three pickers;
   picking a question copies its text into the matching pre-interview editor. */

document.addEventListener('DOMContentLoaded', () => {
    const categorySelect = document.querySelector('#pack-form #id_category');
    if (!categorySelect) return;

    const pickers = [1, 2, 3].map((i) => ({
        select: document.querySelector(`#id_question_${i}`),
        editor: document.querySelector(`#id_pre_interview_question_${i}`),
    }));

    let questionHtml = {};

    function reset(select, message) {
        select.innerHTML = '';
        const option = document.createElement('option');
        option.value = '';
        option.textContent = message;
        select.appendChild(option);
    }

    function fill(select, data) {
        reset(select, 'Select a question');
        data.forEach((question) => {
            const option = document.createElement('option');
            option.value = question.id;
            option.textContent = question.text;
            select.appendChild(option);
        });
    }

    pickers.forEach(({ select, editor }) => {
        if (!select) return;
        reset(select, 'Select category first');

        select.addEventListener('change', () => {
            const html = questionHtml[select.value];
            if (html && editor && hasSummernote()) {
                jQuery(editor).summernote('code', html);
            }
        });
    });

    categorySelect.addEventListener('change', () => {
        if (!categorySelect.value) {
            pickers.forEach(({ select }) => select && reset(select, 'Select category first'));
            return;
        }

        pickers.forEach(({ select }) => select && reset(select, 'Loading...'));

        fetch(`/ajax/load-questions/?category=${encodeURIComponent(categorySelect.value)}`)
            .then((res) => {
                if (!res.ok) throw new Error('Network error');
                return res.json();
            })
            .then((data) => {
                questionHtml = {};
                data.forEach((question) => { questionHtml[question.id] = question.html; });
                pickers.forEach(({ select }) => select && fill(select, data));
            })
            .catch(() => {
                pickers.forEach(({ select }) => select && reset(select, 'Error loading questions'));
            });
    });
});

/* ─────────────────── 9. Add questions: validation ─────────────────── */

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('questions-form');
    if (!form || !hasSummernote()) return;

    form.addEventListener('submit', (event) => {
        const hasQuestion = jQuery('#questions-form .richtext').toArray()
            .some((el) => stripHtml(jQuery(el).summernote('code')));

        if (!hasQuestion) {
            alert('Please enter at least one question.');
            event.preventDefault();
        }
    });
});

/* ─────────────────── 10. Indicators admin page ─────────────────── */

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('indicator-form');
    if (!form || !hasSummernote()) return;

    const existingNames = readJson('indicator-names-data') || [];
    const DRAFT_KEY = 'indicator-form-draft';
    const nameSelect = document.getElementById('name-select');
    const newNameInput = document.getElementById('new-name-input');
    const pairsContainer = document.getElementById('pairs-container');
    const arModal = document.getElementById('ar-modal');
    let pairCount = 0;

    const editorOptions = (placeholder) => ({
        toolbar: SUMMERNOTE_TOOLBAR,
        height: 80,
        placeholder,
        callbacks: { onChange: function (contents) { jQuery(this).val(contents); saveDraft(); } },
    });

    function saveDraft() {
        const draft = { nameSelect: nameSelect.value, newName: newNameInput.value, pairs: [] };
        pairsContainer.querySelectorAll('.pair-row').forEach((row) => {
            const pos = row.querySelector('textarea[name^="positive_"]');
            const neg = row.querySelector('textarea[name^="negative_"]');
            if (pos && neg) {
                draft.pairs.push({
                    pos: jQuery(pos).summernote('code'),
                    neg: jQuery(neg).summernote('code'),
                });
            }
        });
        localStorage.setItem(DRAFT_KEY, JSON.stringify(draft));
    }

    function restoreDraft() {
        const raw = localStorage.getItem(DRAFT_KEY);
        if (!raw) return false;
        try {
            const draft = JSON.parse(raw);
            if (draft.nameSelect) {
                nameSelect.value = draft.nameSelect;
                toggleNewNameInput();
            }
            if (draft.newName) newNameInput.value = draft.newName;
            if (draft.pairs && draft.pairs.length > 0) {
                draft.pairs.forEach((pair) => {
                    addPair();
                    const idx = pairCount - 1;
                    if (pair.pos) jQuery('#pos-' + idx).summernote('code', pair.pos);
                    if (pair.neg) jQuery('#neg-' + idx).summernote('code', pair.neg);
                });
                return true;
            }
        } catch (e) { /* corrupt draft: start fresh */ }
        return false;
    }

    function clearDraft() {
        localStorage.removeItem(DRAFT_KEY);
    }

    function toggleNewNameInput() {
        const isNew = nameSelect.value === '__new__';
        document.getElementById('new-name-wrap').style.display = isNew ? 'block' : 'none';
        if (isNew) newNameInput.focus();
    }

    function addPair() {
        const idx = pairCount++;
        const row = document.createElement('div');
        row.className = 'pair-row';
        row.id = 'pair-' + idx;
        row.innerHTML =
            '<button type="button" class="button is-light is-small remove-btn" data-remove-pair="' + idx + '">✕</button>' +
            '<label class="field-label" style="margin-bottom:0.2rem;">Positive</label>' +
            '<textarea name="positive_' + idx + '" id="pos-' + idx + '"></textarea>' +
            '<label class="field-label" style="margin-top:0.4rem; margin-bottom:0.2rem;">Negative</label>' +
            '<textarea name="negative_' + idx + '" id="neg-' + idx + '"></textarea>';
        pairsContainer.appendChild(row);

        jQuery('#pos-' + idx).summernote(editorOptions('+ Positive behaviour...'));
        jQuery('#neg-' + idx).summernote(editorOptions('− Negative behaviour...'));
    }

    function removePair(idx) {
        const row = document.getElementById('pair-' + idx);
        if (!row) return;
        jQuery('#pos-' + idx).summernote('destroy');
        jQuery('#neg-' + idx).summernote('destroy');
        row.remove();
        saveDraft();
    }

    function resolvedName() {
        return (nameSelect.value === '__new__' ? newNameInput.value : nameSelect.value).trim();
    }

    function submitWith(mode) {
        clearDraft();
        document.getElementById('mode-field').value = mode;
        arModal.classList.remove('active');
        form.submit();
    }

    function handleSave() {
        const name = resolvedName();
        if (!name) { alert('Please select or enter an indicator name.'); return; }

        const hasPair = Array.from(pairsContainer.querySelectorAll('.pair-row')).some((row) => {
            const pos = row.querySelector('textarea[name^="positive_"]');
            const neg = row.querySelector('textarea[name^="negative_"]');
            return (pos && stripHtml(jQuery(pos).summernote('code')))
                || (neg && stripHtml(jQuery(neg).summernote('code')));
        });
        if (!hasPair) { alert('Please add at least one behaviour pair.'); return; }

        document.getElementById('indicator-name-hidden').value = name;

        const isNew = nameSelect.value === '__new__';
        if (!isNew && existingNames.includes(name)) {
            document.getElementById('ar-title').textContent = '"' + name + '" already has behaviour pairs';
            document.getElementById('ar-body').textContent =
                'Add new pairs alongside the existing ones, or replace them all?';
            arModal.classList.add('active');
        } else {
            submitWith('add');
        }
    }

    nameSelect.addEventListener('change', () => { toggleNewNameInput(); saveDraft(); });
    newNameInput.addEventListener('input', saveDraft);
    document.getElementById('add-pair-btn').addEventListener('click', () => addPair());
    document.getElementById('save-indicator-btn').addEventListener('click', handleSave);

    pairsContainer.addEventListener('click', (event) => {
        const button = event.target.closest('[data-remove-pair]');
        if (button) removePair(button.getAttribute('data-remove-pair'));
    });

    arModal.querySelectorAll('[data-ar-mode]').forEach((button) => {
        button.addEventListener('click', () => submitWith(button.getAttribute('data-ar-mode')));
    });
    arModal.addEventListener('click', (event) => {
        if (event.target === arModal) arModal.classList.remove('active');
    });

    if (!restoreDraft()) addPair();
});

/* ─────────────────── 11. Schedule interview: date/time ─────────────────── */

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('interview-schedule-form');
    if (!form) return;

    const datePicker = document.getElementById('date_picker');
    const timePicker = document.getElementById('time_picker');

    function localISO(dateObj = new Date()) {
        const offset = dateObj.getTimezoneOffset();
        return new Date(dateObj.getTime() - offset * 60 * 1000).toISOString();
    }

    function bounds() {
        const now = new Date();
        const iso = localISO(now);
        const maxDate = new Date();
        maxDate.setFullYear(now.getFullYear() + 3);
        return {
            todayStr: iso.split('T')[0],
            currentTimeStr: iso.split('T')[1].substring(0, 5),
            maxDateStr: localISO(maxDate).split('T')[0],
        };
    }

    function updateMinMax() {
        const { todayStr, currentTimeStr, maxDateStr } = bounds();
        datePicker.min = todayStr;
        datePicker.max = maxDateStr;

        if (datePicker.value === todayStr) {
            timePicker.min = currentTimeStr;
        } else {
            timePicker.removeAttribute('min');
        }
    }

    updateMinMax();
    datePicker.addEventListener('change', updateMinMax);

    form.addEventListener('submit', (event) => {
        const { todayStr, currentTimeStr, maxDateStr } = bounds();

        if (datePicker.value === todayStr && timePicker.value < currentTimeStr) {
            event.preventDefault();
            alert("Please pick a future time for today's interview.");
            return;
        }

        if (datePicker.value > maxDateStr) {
            event.preventDefault();
            alert('Interviews cannot be scheduled more than 3 years in the future.');
            return;
        }

        if (datePicker.value && timePicker.value) {
            document.getElementById('interview_date').value = datePicker.value + 'T' + timePicker.value;
        }
    });
});

/* ─────────────────── 12. Interview page ─────────────────── */

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('interview-form');
    if (!form || !hasSummernote()) return;

    const indicatorGroups = readJson('indicator-groups-data') || {};
    const savedIndicatorScores = readJson('saved-indicator-scores-data') || {};
    const savedGroupScores = readJson('saved-group-scores-data') || {};
    const savedGroupNotes = readJson('saved-group-notes-data') || {};

    const editorOptions = (height, placeholder) => ({
        toolbar: [
            ['style', ['bold', 'italic', 'underline']],
            ['para', ['ul', 'ol']],
            ['misc', ['undo', 'redo']],
        ],
        height,
        placeholder,
        callbacks: { onChange: function (contents) { jQuery(this).val(contents); } },
    });

    jQuery('.notes-textarea').summernote(editorOptions(150, 'Enter interview notes here...'));
    jQuery('.feedback-textarea').summernote(editorOptions(120, 'Enter feedback for this question...'));

    /* Pack tabs */
    document.querySelectorAll('[data-pack-tab]').forEach((tab) => {
        tab.addEventListener('click', () => {
            const packId = tab.getAttribute('data-pack-tab');
            document.querySelectorAll('.pack-section').forEach((s) => { s.style.display = 'none'; });
            document.querySelectorAll('.pack-tabs li').forEach((t) => t.classList.remove('is-active'));
            document.getElementById('pack-' + packId).style.display = 'block';
            document.getElementById('tab-' + packId).classList.add('is-active');
        });
    });

    /* Pre-interview answers toggle */
    const answersToggle = document.getElementById('toggle-answers-btn');
    answersToggle?.addEventListener('click', () => {
        const el = document.getElementById('applicant-answers');
        const arrow = document.getElementById('answers-arrow');
        el.style.display = el.style.display === 'none' ? 'block' : 'none';
        arrow.innerHTML = el.style.display === 'none' ? '&#9660;' : '&#9650;';
    });

    /* Indicator picker modal */
    const modal = document.getElementById('indicator-modal');
    const modalBody = document.getElementById('indicator-modal-body');

    function openIndicatorModal() {
        const names = Object.keys(indicatorGroups);
        modalBody.innerHTML = '';

        if (names.length === 0) {
            modalBody.innerHTML =
                '<p class="has-text-grey has-text-centered">No indicators have been created yet.</p>';
        } else {
            const hint = document.createElement('p');
            hint.className = 'is-size-7 has-text-grey mb-3';
            hint.textContent = 'Select an indicator to add its behaviour pairs to the assessment.';
            modalBody.appendChild(hint);

            names.forEach((name) => {
                const behaviours = indicatorGroups[name];
                const alreadyAdded = behaviours.every((b) => document.getElementById('ind-row-' + b.id));

                const card = document.createElement('div');
                card.className = 'box mb-3 indicator-card' + (alreadyAdded ? ' has-background-light' : '');
                card.style.cursor = alreadyAdded ? 'default' : 'pointer';
                card.innerHTML =
                    '<div style="display:flex; justify-content:space-between; align-items:start;">' +
                    '<div>' +
                    '<p class="has-text-weight-bold">' + escHtml(name) + '</p>' +
                    '<p class="is-size-7 has-text-grey">' + behaviours.length + ' behaviour pair' + (behaviours.length !== 1 ? 's' : '') + '</p>' +
                    behaviours.map((b) =>
                        '<p class="is-size-7 indicator-positive mt-1">+ ' + escHtml(stripHtml(b.positive).slice(0, 80)) + '</p>' +
                        '<p class="is-size-7 indicator-negative">− ' + escHtml(stripHtml(b.negative).slice(0, 80)) + '</p>'
                    ).join('') +
                    '</div>' +
                    (alreadyAdded
                        ? '<span class="tag is-light ml-3">Added</span>'
                        : '<span class="button is-small is-primary ml-3" style="pointer-events:none;">Add</span>') +
                    '</div>';

                if (!alreadyAdded) {
                    card.addEventListener('click', () => addIndicatorGroup(name));
                }
                modalBody.appendChild(card);
            });
        }

        modal.classList.add('is-active');
    }

    function closeIndicatorModal() {
        modal.classList.remove('is-active');
    }

    function groupElemId(name) {
        return 'ind-group-' + name.replace(/[^a-zA-Z0-9]/g, '_');
    }

    function addIndicatorGroup(name) {
        const behaviours = indicatorGroups[name];
        if (!behaviours) return;

        const gid = groupElemId(name);
        if (!document.getElementById(gid)) {
            const section = document.createElement('div');
            section.id = gid;
            section.className = 'mb-4';
            section.innerHTML =
                '<p class="has-text-weight-semibold mb-2" style="color:#1800A8;">' + escHtml(name) + '</p>' +
                '<table class="score-table" style="width:100%;">' +
                '<thead><tr><th>Positive</th><th>Negative</th><th>Score (1–6)</th></tr></thead>' +
                '<tbody id="' + gid + '-tbody"></tbody>' +
                '<tfoot><tr style="border-top:2px solid #e0e0e0;">' +
                '<td colspan="2" style="padding:0.5rem 0.75rem; font-weight:700;">Overall Score</td>' +
                '<td style="padding:0.4rem 0.75rem;">' +
                '<input type="number" min="1" max="6" step="1" class="score-input"' +
                ' name="group_score_' + escHtml(name) + '" id="' + gid + '-overall" placeholder="1–6" required>' +
                '</td></tr></tfoot></table>' +
                '<textarea class="textarea is-small mt-2" name="group_notes_' + escHtml(name) + '"' +
                ' id="' + gid + '-notes" placeholder="Notes for ' + escHtml(name) + '..."></textarea>';
            document.getElementById('indicator-groups-container').appendChild(section);

            jQuery('#' + gid + '-notes').summernote(editorOptions(100, 'Notes for ' + name + '...'));

            if (savedGroupScores[name] !== undefined) {
                document.getElementById(gid + '-overall').value = savedGroupScores[name];
            }
            if (savedGroupNotes[name]) {
                jQuery('#' + gid + '-notes').summernote('code', savedGroupNotes[name]);
            }
        }

        const tbody = document.getElementById(gid + '-tbody');
        behaviours.forEach((b) => {
            if (document.getElementById('ind-row-' + b.id)) return;
            const row = document.createElement('tr');
            row.id = 'ind-row-' + b.id;
            row.innerHTML =
                '<td class="indicator-positive">' + b.positive + '</td>' +
                '<td class="indicator-negative">' + b.negative + '</td>' +
                '<td><input type="number" min="1" max="6" step="1" class="score-input"' +
                ' name="indicator_score_' + b.id + '" placeholder="1–6" required></td>';
            tbody.appendChild(row);
        });

        document.getElementById('indicator-table-wrap').style.display = 'block';
        closeIndicatorModal();
    }

    document.getElementById('open-indicator-modal-btn')?.addEventListener('click', openIndicatorModal);
    modal.querySelector('.modal-background').addEventListener('click', closeIndicatorModal);
    modal.querySelector('.delete').addEventListener('click', closeIndicatorModal);

    /* Restore previously saved indicator scores (autosave / revisit). */
    if (Object.keys(savedIndicatorScores).length > 0) {
        const indicatorToGroup = {};
        Object.keys(indicatorGroups).forEach((name) => {
            indicatorGroups[name].forEach((b) => { indicatorToGroup[b.id] = name; });
        });

        const groupsAdded = new Set();
        Object.keys(savedIndicatorScores).forEach((idStr) => {
            const name = indicatorToGroup[parseInt(idStr, 10)];
            if (name && !groupsAdded.has(name)) {
                addIndicatorGroup(name);
                groupsAdded.add(name);
            }
        });

        Object.keys(savedIndicatorScores).forEach((idStr) => {
            const input = document.getElementById('ind-row-' + idStr)?.querySelector('input[type="number"]');
            if (input) input.value = savedIndicatorScores[idStr];
        });
    }

    /* Clamp every 1–6 score input as it's typed. */
    form.addEventListener('input', (event) => {
        if (event.target.classList.contains('score-input') && event.target.value !== '') {
            const val = parseInt(event.target.value, 10);
            if (!isNaN(val)) {
                if (val > 6) event.target.value = 6;
                else if (val < 1) event.target.value = 1;
            }
        }
    }, true);

    /* Keep the hidden textareas in sync with the editors. */
    function syncSummernotes() {
        jQuery('.notes-textarea, .feedback-textarea').each(function () {
            jQuery(this).val(jQuery(this).summernote('code'));
        });
        document.querySelectorAll('#indicator-groups-container textarea').forEach((ta) => {
            if (jQuery(ta).data('summernote')) {
                jQuery(ta).val(jQuery(ta).summernote('code'));
            }
        });
    }

    form.addEventListener('submit', (event) => {
        syncSummernotes();

        const emptyNotes = jQuery('.notes-textarea').toArray()
            .some((el) => !stripHtml(jQuery(el).summernote('code')));
        if (emptyNotes) {
            alert('Please fill in all notes before submitting.');
            event.preventDefault();
            return;
        }

        const emptyFeedback = jQuery('.feedback-textarea').toArray()
            .some((el) => !stripHtml(jQuery(el).summernote('code')));
        if (emptyFeedback) {
            alert('Please fill in all feedback before submitting.');
            event.preventDefault();
        }
    });

    /* Autosave every 30 seconds. */
    const autosaveUrl = form.getAttribute('data-autosave-url');
    const autosaveStatus = document.getElementById('autosave-status');

    function autosave() {
        syncSummernotes();
        autosaveStatus.textContent = 'Saving…';
        fetch(autosaveUrl, { method: 'POST', body: new FormData(form) })
            .then((r) => r.json())
            .then((d) => {
                autosaveStatus.textContent = d.ok ? '✓ Saved' : 'Save failed';
                setTimeout(() => { autosaveStatus.textContent = ''; }, 3000);
            })
            .catch(() => {
                autosaveStatus.textContent = 'Save failed';
                setTimeout(() => { autosaveStatus.textContent = ''; }, 3000);
            });
    }

    setInterval(autosave, 30000);
});
