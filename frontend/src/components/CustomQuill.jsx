import React, { useEffect, useRef } from "react";
import ReactQuill from "react-quill";
import "react-quill/dist/quill.snow.css";
import PropTypes from "prop-types";
const Quill = ReactQuill.Quill;
const Font = Quill.import("formats/font");
Font.whitelist = ["yekan", "sans-serif"];
Quill.register(Font, true);

const CustomQuill = ({ isReadOnly, value, handleDataChange }) => {
  let isProgrammaticUpdate = false;
  const quillRef = useRef(null);
  useEffect(() => {
    if (quillRef.current) {
      const quill = quillRef.current.getEditor();
      isProgrammaticUpdate = true;
      quill.setText(" ");

      quill.format("size", "large");
      quill.format("direction", "rtl");
      quill.format("align", "right");
      quill.format("font", "yekan");

      quill.deleteText(0, 1);
      isProgrammaticUpdate = false;
    }
  }, []);
  const handleContentChange = (value, delta, source, editor) => {
    handleDataChange(value);
    if (isProgrammaticUpdate) {
      return;
    }
    if (editor.getLength() <= 1 && quillRef.current) {
      const quill = quillRef.current.getEditor();
      isProgrammaticUpdate = true;
      quill.setText(" ");

      quill.format("size", "large");
      quill.format("direction", "rtl");
      quill.format("align", "right");
      quill.format("font", "yekan");

      quill.deleteText(0, 1);
      isProgrammaticUpdate = false;
    }
  };
  return (
    <ReactQuill
      ref={quillRef}
      value={value}
      onChange={handleContentChange}
      placeholder="محتوا"
      readOnly={isReadOnly}
      modules={{
        toolbar: [
          ["bold", "italic", "underline", "strike"],
          [{ header: 1 }, { header: 2 }],
          [{ list: "ordered" }, { list: "bullet" }],
          [{ script: "sub" }, { script: "super" }],
          [{ size: ["small", false, "large", "huge"] }],
          [{ indent: "-1" }, { indent: "+1" }],
          [{ direction: "rtl" }],
          [{ align: [] }],
          [{ header: [1, 2, 3, 4, 5, 6, false] }],
          [{ color: [] }, { background: [] }],
          [{ font: Font.whitelist }],
          ["link", "image", "blockquote", "code-block"],
        ],
      }}
      formats={[
        "header",
        "font",
        "size",
        "bold",
        "italic",
        "direction",
        "align",
        "underline",
        "strike",
        "blockquote",
        "list",
        "bullet",
        "indent",
        "link",
        "image",
        "color",
        "background",
        "code-block",
        "script",
      ]}
      style={{
        width: "100%",
        marginBottom: 10,
        direction: "ltr",
      }}
    />
  );
};

CustomQuill.propTypes = {
  isReadOnly: PropTypes.bool,
  value: PropTypes.string,
  handleDataChange: PropTypes.func,
};

CustomQuill.defaultProps = {
  isReadOnly: false,
  value: "",
  handleDataChange: () => {},
};

export default CustomQuill;
