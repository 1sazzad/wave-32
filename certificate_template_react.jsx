import React from "react";
import "./certificate_template.css";

/**
 * React version of the same certificate design used by certificate_template.html.
 * Pass dynamic fields via props to render any participant certificate.
 */
export default function CertificateTemplate({ data }) {
  return (
    <div className="certificate">
      <div
        className="bg"
        style={{ backgroundImage: `url(${data.background_image || "certificate_design.png"})` }}
      />
      <div className="overlay">
        <img src={data.left_logo} className="logo-left" alt="Left logo" />
        <img src={data.right_logo} className="logo-right" alt="Right logo" />

        <div className="header">{data.org_header}</div>
        <div className="sub-header">{data.org_subheader}</div>
        <div className="title">{data.certificate_title}</div>

        <div className="subtitle-wrap">
          <span className="subtitle-line" />
          <span className="subtitle-dot" />
          <span className="subtitle">{data.certificate_subtitle}</span>
          <span className="subtitle-dot" />
          <span className="subtitle-line" />
        </div>

        <div className="presented">{data.presented_line}</div>
        <div className="name">{data.participant_name}</div>
        <div className="name-rule" />

        <div className="desc">{data.participation_line}</div>
        <div className="contest">{data.contest_name}</div>

        <div className="details">
          {data.detail_line_1}
          <br />
          {data.detail_line_2}
        </div>

        <div className="team">{data.team_line}</div>

        <div className="signature-left">
          <img src={data.president_signature} className="sig-img" alt="President signature" />
          <div className="sig-line" />
          <div className="sig-name">{data.president_name}</div>
          <div className="sig-title">{data.president_title}</div>
        </div>

        <div className="signature-right">
          <img src={data.dept_head_signature} className="sig-img" alt="Dept head signature" />
          <div className="sig-line" />
          <div className="sig-name">{data.dept_head_name}</div>
          <div className="sig-title">{data.dept_head_title}</div>
        </div>

        <div className="middle-separator" />
        <div className="emblem">❦ ★ ★ ★ ❦</div>

        <div className="cert-id">CERTIFICATE ID: {data.certificate_id}</div>
      </div>
    </div>
  );
}
