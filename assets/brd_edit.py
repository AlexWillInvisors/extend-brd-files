#!/usr/bin/env python3
"""
brd_edit.py — safe, tree-based editing for the Invisors Extend BRD template.

WHY THIS EXISTS
String-splicing document.xml (replacing a <w:r>...<w:t>X</w:t></w:r> and appending
"</w:r></w:p><w:p>...") repeatedly produces orphaned closing tags and run-in-run
nesting that only surface at pack-time schema validation. Every operation here works
on a parsed lxml tree instead, so the output is always well-formed and schema-legal
by construction. Use this for ALL content insertion and tracked-change edits; do not
hand-splice the XML.

USAGE (import as a module from a fill script):

    from brd_edit import BRD
    doc = BRD("unpacked/word/document.xml")

    # replace the visible text of the run that currently contains a placeholder
    doc.set_run_text("Summary of our understanding", "Real BR opening prose...")

    # insert new sibling paragraphs AFTER the paragraph containing an anchor string
    doc.add_paragraphs_after(
        "The problems this solution bridges:",
        [
            {"style": "ListParagraph", "num": 5, "runs": [("bullet one text", False)]},
            {"style": "ListParagraph", "num": 5, "runs": [("bullet two text", False)]},
        ],
    )

    # fill an empty table cell paragraph (by the cell's first <w:p> paraId, or by
    # locating an empty data row in a table found via a header anchor)
    doc.fill_table_rows("The following integrations", header_anchor=True, rows=[
        [("Name", False)], ... ])  # see fill_table_rows docstring

    # tracked-change: replace a phrase, marking deletion + insertion as "Claude"
    doc.tracked_replace("retention policy considerations (e.g., 7 years)",
                        "retention period of 7 years")

    doc.save()  # writes back; then pack with the docx skill and VALIDATE

ALWAYS run doc.lint() before save() — it asserts every <w:r> sits in a legal parent
and every <w:p> is a legal child, catching structure errors before pack-time.
"""

import re
import sys
from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
def w(tag): return f"{{{W}}}{tag}"
NSMAP = {"w": W}

# legal parents for a <w:r> (run); legal parents for a <w:p> (paragraph)
RUN_OK_PARENTS = {w("p"), w("ins"), w("del"), w("hyperlink"), w("smartTag"),
                  w("fldSimple"), w("dir"), w("bdo"), w("sdtContent")}
PARA_OK_PARENTS = {w("body"), w("tc"), w("txbxContent"), w("hdr"), w("ftr"),
                   w("sdtContent"), w("comment"), w("footnote"), w("endnote")}

TRACK_AUTHOR = "Claude"
TRACK_DATE = "2026-01-01T00:00:00Z"


def _escape(t):
    # lxml handles escaping when we set .text; this is only for sanity on raw use
    return t


class BRD:
    def __init__(self, path):
        self.path = path
        parser = etree.XMLParser(remove_blank_text=False)
        self.tree = etree.parse(path, parser)
        self.root = self.tree.getroot()
        self._ins_id = 1000  # tracked-change id counter
        self._merged = False  # set once merge_runs() has run (lazy fallback)
        self._w14 = 0x200000  # counter for fresh w14:paraId/textId (kept < 0x80000000)

    # ---- run-merge (self-sufficiency: do what the docx skill's unpack.py does) ----
    # A placeholder authored in Word is often split across several <w:r> runs that
    # differ only by revision id (w:rsidR), e.g. "S"+"ummary of our "+"understanding".
    # The text-anchor finders need the phrase contiguous in one <w:t>. unpack.py merges
    # such runs; merge_runs() does the same so this helper works with OR without it.
    _MERGE_OK_CHILDREN = frozenset({w("rPr"), w("t")})
    # Spell/grammar-check range markers Word sprinkles BETWEEN runs (e.g. spellStart
    # around "BoW"). They carry no content, only squiggly underlines, and they break
    # run adjacency. Treat them as transparent and drop them during a merge.
    _TRANSPARENT = frozenset({w("proofErr")})

    def _mergeable(self, r):
        """A run is mergeable only if it carries nothing but rPr/text — never merge a
        run holding a break, tab, drawing, field, or footnote ref."""
        return all(c.tag in self._MERGE_OK_CHILDREN for c in r)

    def _rpr_key(self, r):
        # Compare run properties by CONTENT, not raw serialization: a sub-element's
        # tostring() carries inherited namespace declarations (xmlns:a, xmlns:wpc, …)
        # that vary by document position, so two identical rPr would look different.
        # Exclusive C14N drops unused namespace decls and sorts attributes, so equal
        # properties compare equal (this is what lets the split title runs merge).
        rpr = r.find(w("rPr"))
        if rpr is None:
            return b""
        try:
            return etree.tostring(rpr, method="c14n", exclusive=True)
        except (TypeError, ValueError):
            return etree.tostring(rpr)

    def _append_text(self, dst, src):
        dt = dst.find(w("t"))
        st = src.find(w("t"))
        s_text = st.text if (st is not None and st.text) else ""
        if dt is None:
            dt = etree.SubElement(dst, w("t"))
            dt.text = ""
        dt.text = (dt.text or "") + s_text
        dt.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")

    def merge_runs(self):
        """Merge adjacent sibling <w:r> runs that share identical run properties (rPr),
        ignoring revision ids. Only merges direct children of a <w:p> (so runs inside
        <w:ins>/<w:del>/<w:hyperlink> are left alone) and only runs that hold nothing
        but rPr/text. Idempotent and semantically invisible — it consolidates runs
        without changing rendered text or formatting."""
        R = w("r")
        for p in self.root.iter(w("p")):
            prev = None
            for child in list(p):
                if child.tag in self._TRANSPARENT:
                    p.remove(child)  # drop the marker; do NOT break the merge chain
                    continue
                if child.tag == R and self._mergeable(child):
                    if prev is not None and self._rpr_key(prev) == self._rpr_key(child):
                        self._append_text(prev, child)
                        p.remove(child)
                    else:
                        prev = child
                else:
                    prev = None
        self._merged = True
        return self

    def _ensure_merged(self):
        if not self._merged:
            self.merge_runs()

    # ---- helpers to build elements ----
    def _run(self, text, bold=False, sz="20"):
        r = etree.SubElement(etree.Element(w("tmp")), w("r"))
        rpr = etree.SubElement(r, w("rPr"))
        if bold:
            etree.SubElement(rpr, w("b"))
        if sz:
            etree.SubElement(rpr, w("sz")).set(w("val"), sz)
            etree.SubElement(rpr, w("szCs")).set(w("val"), sz)
        if len(rpr) == 0:
            r.remove(rpr)
        t = etree.SubElement(r, w("t"))
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        t.text = text
        return r

    def _para(self, runs, style=None, num=None, sz="20"):
        """runs: list of (text, bold) tuples."""
        p = etree.Element(w("p"))
        if style or num is not None:
            ppr = etree.SubElement(p, w("pPr"))
            if style:
                etree.SubElement(ppr, w("pStyle")).set(w("val"), style)
            if num is not None:
                numpr = etree.SubElement(ppr, w("numPr"))
                etree.SubElement(numpr, w("ilvl")).set(w("val"), "0")
                etree.SubElement(numpr, w("numId")).set(w("val"), str(num))
        for text, bold in runs:
            p.append(self._run(text, bold=bold, sz=sz))
        return p

    # ---- text-finding ----
    def _find_run_with_text(self, needle):
        for t in self.root.iter(w("t")):
            if t.text and needle in t.text:
                return t
        self._ensure_merged()  # retry once after merging split runs
        for t in self.root.iter(w("t")):
            if t.text and needle in t.text:
                return t
        return None

    def _find_para_with_text(self, needle):
        t = self._find_run_with_text(needle)
        if t is None:
            return None
        p = t
        while p is not None and p.tag != w("p"):
            p = p.getparent()
        return p

    # ---- public operations ----
    def set_run_text(self, needle, new_text):
        """Replace the full .text of the <w:t> that contains `needle`. Single match."""
        matches = [t for t in self.root.iter(w("t")) if t.text and needle in t.text]
        if len(matches) != 1:
            self._ensure_merged()  # placeholder may be split across runs
            matches = [t for t in self.root.iter(w("t")) if t.text and needle in t.text]
        assert len(matches) == 1, f"set_run_text: {len(matches)} matches for {needle!r}"
        matches[0].text = new_text
        return self

    def replace_paragraph_runs(self, needle, runs, keep_ppr=True, sz="20"):
        """Replace ALL runs in the paragraph containing `needle` with new runs.
        Preserves the paragraph's <w:pPr>. runs: list of (text, bold)."""
        p = self._find_para_with_text(needle)
        assert p is not None, f"replace_paragraph_runs: no paragraph for {needle!r}"
        ppr = p.find(w("pPr"))
        for child in list(p):
            if child.tag == w("pPr") and keep_ppr:
                continue
            p.remove(child)
        for text, bold in runs:
            p.append(self._run(text, bold=bold, sz=sz))
        return self

    def add_paragraphs_after(self, needle, paras, sz="20"):
        """Insert new sibling paragraphs immediately after the paragraph containing
        `needle`. paras: list of dicts {runs:[(text,bold)], style?:str, num?:int}."""
        anchor = self._find_para_with_text(needle)
        assert anchor is not None, f"add_paragraphs_after: no paragraph for {needle!r}"
        parent = anchor.getparent()
        idx = list(parent).index(anchor)
        for offset, spec in enumerate(paras, start=1):
            p = self._para(spec["runs"], style=spec.get("style"),
                           num=spec.get("num"), sz=sz)
            parent.insert(idx + offset, p)
        return self

    def fill_empty_cell(self, para_id, runs, sz="20"):
        """Fill an empty cell paragraph identified by its w14:paraId."""
        PID = "{http://schemas.microsoft.com/office/word/2010/wordml}paraId"
        target = None
        for p in self.root.iter(w("p")):
            if p.get(PID) == para_id:
                target = p
                break
        assert target is not None, f"fill_empty_cell: no paragraph paraId={para_id}"
        for text, bold in runs:
            target.append(self._run(text, bold=bold, sz=sz))
        return self

    def fill_table_rows(self, header_anchor, rows, sz="20"):
        """Find the table associated with `header_anchor`, clone its first data row
        once per entry in `rows`, and fill each cell. The anchor may be either text
        inside the table's header row OR intro text in the paragraph immediately
        preceding the table. `rows` is a list of rows; each row a list of cells;
        each cell a list of (text,bold) runs. Replaces existing data rows entirely."""
        import copy
        ht = self._find_run_with_text(header_anchor)
        assert ht is not None, f"fill_table_rows: anchor {header_anchor!r} not found"
        # walk up looking for an enclosing tbl
        node = ht
        while node is not None and node.tag != w("tbl"):
            node = node.getparent()
        tbl = node
        if tbl is None:
            # anchor is outside any table (e.g. an intro sentence) — find the next
            # <w:tbl> sibling that appears after the anchor's paragraph in document order
            anchor_p = self._find_para_with_text(header_anchor)
            all_tbls = list(self.root.iter(w("tbl")))
            anchor_pos = self._doc_order_index(anchor_p)
            following = [t for t in all_tbls if self._doc_order_index(t) > anchor_pos]
            assert following, f"fill_table_rows: no table after anchor {header_anchor!r}"
            tbl = following[0]
        trs = tbl.findall(w("tr"))
        assert len(trs) >= 2, "fill_table_rows: need header + >=1 data row"
        template_row = trs[1]
        for tr in trs[1:]:
            tbl.remove(tr)
        for row in rows:
            new_tr = copy.deepcopy(template_row)
            cells = new_tr.findall(w("tc"))
            assert len(cells) == len(row), \
                f"fill_table_rows: row has {len(row)} cells, table has {len(cells)}"
            for tc, cell_runs in zip(cells, row):
                p = tc.find(w("p"))
                for child in list(p):
                    if child.tag != w("pPr"):
                        p.remove(child)
                for text, bold in cell_runs:
                    p.append(self._run(text, bold=bold, sz=sz))
                for extra in tc.findall(w("p"))[1:]:
                    tc.remove(extra)
            tbl.append(new_tr)
        return self

    def _doc_order_index(self, el):
        """Position of an element in document order (for 'is X after Y' tests)."""
        for i, node in enumerate(self.root.iter()):
            if node is el:
                return i
        return -1

    # ---- process (use-case) tables + safe block cloning ----
    # The use-case tables are vertical label/value tables (not header+data-row), so
    # fill_table_rows doesn't fit them. These helpers fill them by row label and clone
    # whole tables with VALID fresh ids (hand-rolled random paraIds can land >=
    # 0x80000000, which pack-time validation rejects — this owns id generation instead).
    W14 = "http://schemas.microsoft.com/office/word/2010/wordml"

    def _w14_attr(self, name):
        return f"{{{self.W14}}}{name}"

    def _fresh_w14_id(self):
        """A fresh w14 id as 8 upper-hex chars, guaranteed < 0x80000000."""
        self._w14 += 1
        return format(self._w14 & 0x7FFFFFFF, "08X")

    def clone_block_with_fresh_ids(self, el):
        """Deep-copy any block (e.g. a <w:tbl>) and regenerate every w14:paraId /
        w14:textId so the copy is unique and in the valid id range. Returns the clone
        (not yet inserted)."""
        import copy
        clone = copy.deepcopy(el)
        for node in clone.iter():
            for attr in (self._w14_attr("paraId"), self._w14_attr("textId")):
                if node.get(attr) is not None:
                    node.set(attr, self._fresh_w14_id())
        return clone

    @staticmethod
    def _canon_label(s):
        return re.sub(r"\s+", " ", (s or "").strip().lower()).rstrip(".")

    def _row_first_cell_text(self, tr):
        tcs = tr.findall(w("tc"))
        if not tcs:
            return ""
        return "".join(t.text or "" for t in tcs[0].iter(w("t")))

    def find_process_tables(self):
        """Return the use-case tables (identified structurally: they carry both a
        'Goal' row and a 'Flow of Events' row), in document order."""
        out = []
        for tbl in self.root.iter(w("tbl")):
            cl = {self._canon_label(self._row_first_cell_text(tr)) for tr in tbl.findall(w("tr"))}
            if "goal" in cl and "flow of events" in cl:
                out.append(tbl)
        return out

    _TITLE_KEYS = {"feature", "feature #", "process", "process #", "number", "title", "#"}

    def fill_process_table(self, tbl, fields):
        """Fill a use-case table's value cells by matching each row's label.

        `fields` maps a row label to a value; matching is case-insensitive on the
        label. Recognized labels: the title row ("Feature #"/"Feature"/"title"), Goal,
        Business Event/Trigger, Primary Actor(s), Actor(s), Pre-conditions,
        Post-conditions, Flow of Events. A value may be:
          - a str                       -> one paragraph
          - a list of str               -> one paragraph per string
          - a list of (text, bold)      -> one paragraph with those runs
          - a list of [(text,bold), …]  -> one paragraph per inner run-list
        The last form is how Flow of Events gets one bolded-and-bodied paragraph per
        step. `tbl` is a table element (e.g. from find_process_tables())."""
        norm = {self._canon_label(k): v for k, v in fields.items()}
        for tr in tbl.findall(w("tr")):
            tcs = tr.findall(w("tc"))
            if len(tcs) < 2:
                continue
            label = self._canon_label(self._row_first_cell_text(tr))
            val = norm.get(label)
            if val is None and label in self._TITLE_KEYS:
                for tk in ("feature #", "feature", "process #", "process", "number", "title"):
                    if tk in norm:
                        val = norm[tk]
                        break
            if val is None:
                continue
            self._set_cell(tcs[1], val)
        return self

    def _normalize_cell(self, val):
        """Coerce a fill value into a list of paragraphs, each a list of (text, bold)."""
        if isinstance(val, str):
            return [[(val, False)]]
        if isinstance(val, (list, tuple)):
            if not val:
                return [[("", False)]]
            first = val[0]
            if isinstance(first, str):
                return [[(s, False)] for s in val]
            if isinstance(first, tuple):
                return [list(val)]
            if isinstance(first, list):
                return [list(p) for p in val]
        return [[(str(val), False)]]

    def _set_cell(self, tc, val, sz="20"):
        """Replace a table cell's paragraphs with the given value, preserving the
        cell's first-paragraph formatting (<w:pPr>)."""
        import copy
        paras = self._normalize_cell(val)
        existing = tc.findall(w("p"))
        ppr = existing[0].find(w("pPr")) if existing else None
        for p in existing:
            tc.remove(p)
        for para in paras:
            np = etree.SubElement(tc, w("p"))
            if ppr is not None:
                np.append(copy.deepcopy(ppr))
            for text, bold in para:
                np.append(self._run(text, bold=bold, sz=sz))
        return self

    def _blank_para(self):
        """An empty paragraph — used to separate tables (see add_process_table)."""
        return etree.Element(w("p"))

    def add_process_table(self, after=None, template=None):
        """Clone a use-case table (the last existing one, or `template`) with fresh
        ids and insert it, ALWAYS separated from neighbouring tables by a paragraph.
        Returns the new <w:tbl> so you can fill_process_table() it.

        Critical: two adjacent <w:tbl> with no paragraph between them MERGE into one
        table in Word (the second inherits the first's banding/shading). So this
        inserts after the paragraph that follows the source table (usually its flow-
        diagram slot) when there is one, and otherwise injects a separator paragraph —
        and guarantees a paragraph follows the clone too. Add a real
        '[[Insert Feature Flow Diagram]]' paragraph after it yourself if the section
        needs one."""
        tbls = self.find_process_tables()
        src = template if template is not None else (tbls[-1] if tbls else None)
        assert src is not None, "add_process_table: no use-case table to clone"
        new = self.clone_block_with_fresh_ids(src)
        if after is None:
            nxt = src.getnext()
            after = nxt if (nxt is not None and nxt.tag == w("p")) else src
        if after.tag == w("tbl"):              # anchor is a table -> need a separator
            sep = self._blank_para()
            after.addnext(sep)
            after = sep
        after.addnext(new)
        nn = new.getnext()                     # guarantee a paragraph follows the clone
        if nn is None or nn.tag == w("tbl"):
            new.addnext(self._blank_para())
        return new

    # ---- tracked changes ----
    def _next_id(self):
        self._ins_id += 1
        return str(self._ins_id)

    def tracked_replace(self, old_text, new_text):
        """Tracked-change replace: find the run whose <w:t> contains old_text, split
        it so old_text becomes a <w:del> and new_text an adjacent <w:ins>, both
        authored as Claude. Surrounding text in the same run is preserved as plain
        runs. Single match."""
        matches = [t for t in self.root.iter(w("t")) if t.text and old_text in t.text]
        if len(matches) != 1:
            self._ensure_merged()  # old_text may be split across runs
            matches = [t for t in self.root.iter(w("t")) if t.text and old_text in t.text]
        assert len(matches) == 1, f"tracked_replace: {len(matches)} matches for {old_text!r}"
        t = matches[0]
        r = t.getparent()                 # the <w:r>
        p = r.getparent()                 # the <w:p> (or ins/del/hyperlink)
        rpr = r.find(w("rPr"))
        before, _, after = t.text.partition(old_text)
        idx = list(p).index(r)
        p.remove(r)
        new_nodes = []
        if before:
            new_nodes.append(self._plain_run(before, rpr))
        new_nodes.append(self._del_run(old_text, rpr))
        new_nodes.append(self._ins_run(new_text, rpr))
        if after:
            new_nodes.append(self._plain_run(after, rpr))
        for offset, node in enumerate(new_nodes):
            p.insert(idx + offset, node)
        return self

    def tracked_insert_paragraphs_after(self, needle, paras, sz="20"):
        """Insert new paragraphs after the paragraph with `needle`, each wholly
        wrapped as a tracked insertion (so reviewers can accept/reject)."""
        anchor = self._find_para_with_text(needle)
        assert anchor is not None, f"tracked_insert: no paragraph for {needle!r}"
        parent = anchor.getparent()
        idx = list(parent).index(anchor)
        for offset, spec in enumerate(paras, start=1):
            p = etree.Element(w("p"))
            ppr = etree.SubElement(p, w("pPr"))
            if spec.get("style"):
                etree.SubElement(ppr, w("pStyle")).set(w("val"), spec["style"])
            if spec.get("num") is not None:
                numpr = etree.SubElement(ppr, w("numPr"))
                etree.SubElement(numpr, w("ilvl")).set(w("val"), "0")
                etree.SubElement(numpr, w("numId")).set(w("val"), str(spec["num"]))
            # mark the paragraph mark itself as inserted
            mrpr = etree.SubElement(ppr, w("rPr"))
            ins_mark = etree.SubElement(mrpr, w("ins"))
            ins_mark.set(w("id"), self._next_id())
            ins_mark.set(w("author"), TRACK_AUTHOR)
            ins_mark.set(w("date"), TRACK_DATE)
            for text, bold in spec["runs"]:
                p.append(self._ins_run(text, None, bold=bold, sz=sz))
            parent.insert(idx + offset, p)
        return self

    def _plain_run(self, text, rpr_template):
        r = etree.Element(w("r"))
        if rpr_template is not None:
            import copy
            r.append(copy.deepcopy(rpr_template))
        tt = etree.SubElement(r, w("t"))
        tt.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        tt.text = text
        return r

    def _del_run(self, text, rpr_template):
        d = etree.Element(w("del"))
        d.set(w("id"), self._next_id())
        d.set(w("author"), TRACK_AUTHOR)
        d.set(w("date"), TRACK_DATE)
        r = etree.SubElement(d, w("r"))
        if rpr_template is not None:
            import copy
            r.append(copy.deepcopy(rpr_template))
        dt = etree.SubElement(r, w("delText"))
        dt.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        dt.text = text
        return d

    def _ins_run(self, text, rpr_template, bold=False, sz=None):
        ins = etree.Element(w("ins"))
        ins.set(w("id"), self._next_id())
        ins.set(w("author"), TRACK_AUTHOR)
        ins.set(w("date"), TRACK_DATE)
        r = etree.SubElement(ins, w("r"))
        if rpr_template is not None:
            import copy
            r.append(copy.deepcopy(rpr_template))
        elif bold or sz:
            rpr = etree.SubElement(r, w("rPr"))
            if bold:
                etree.SubElement(rpr, w("b"))
            if sz:
                etree.SubElement(rpr, w("sz")).set(w("val"), sz)
                etree.SubElement(rpr, w("szCs")).set(w("val"), sz)
        tt = etree.SubElement(r, w("t"))
        tt.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        tt.text = text
        return ins

    # ---- validation ----
    def lint(self):
        """Assert structural legality before saving. Raises on the exact failure
        classes that bit the string-splice approach: run-in-run, run as a direct
        child of body/tc/tr, paragraph in an illegal parent."""
        problems = []
        for r in self.root.iter(w("r")):
            parent = r.getparent()
            if parent.tag not in RUN_OK_PARENTS:
                problems.append(f"<w:r> in illegal parent <{etree.QName(parent).localname}>: "
                                f"{''.join(r.itertext())[:60]!r}")
        for p in self.root.iter(w("p")):
            parent = p.getparent()
            if parent.tag not in PARA_OK_PARENTS:
                problems.append(f"<w:p> in illegal parent <{etree.QName(parent).localname}>")
        if problems:
            raise AssertionError("lint failed:\n  " + "\n  ".join(problems[:10]))
        return self

    def save(self, path=None):
        self.lint()
        out = path or self.path
        self.tree.write(out, xml_declaration=True, encoding="UTF-8", standalone=True)
        return out


if __name__ == "__main__":
    # smoke test: load, lint, report
    if len(sys.argv) > 1:
        doc = BRD(sys.argv[1])
        doc.lint()
        nps = len(list(doc.root.iter(w("p"))))
        print(f"loaded {sys.argv[1]}: {nps} paragraphs, lint OK")
