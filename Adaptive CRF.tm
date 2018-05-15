<TeXmacs|1.99.5>

<style|<tuple|article|varsession>>

<\body>
  <\hide-preamble>
    \;

    <assign|description-aligned|<\macro|body>
      <list|<macro|name|<aligned-item|<item-strong|<arg|name>.>>>|<macro|name|<with|mode|math|<with|font-series|bold|math-font-series|bold|<rigid|\<ast\>>>>>|<arg|body>>
    </macro>>
  </hide-preamble>

  <doc-data|<doc-title|Adaptive CRF Formula
  Derivation>|<doc-author|<author-data|<author-name|Kilo19>>>>

  You have a H.264 source that you wanna compress to a lower target bitrate
  with similar quality settings (motion estimation, I/P/B frame placement,
  etc, the presets (not to be confused with output quality)). You can do
  1-pass average bitrate (bad quality) or 2-pass average bitrate (slow).
  Werner Robitza suggests that a good compromise is to use CRF with VBV to
  constrain bitrate (Understanding Rate Control Modes (x264, x265),
  http://slhck.info/video/2017/03/01/rate-control.html). The author wrote the
  following about CRF+VBV:

  \P

  When you apply VBV to CRF encoding, the trick is to find a CRF value that,
  on average, results in your desired maximum bitrate, but not more. If your
  encode always \Pmaxes out\Q your maximum bitrate, your CRF was probably set
  too low. In such a case the encoder tries to spend bits it doesn't have. On
  the other hand, if you have a high CRF that makes the bitrate not always
  hit the maximum, you could still lower it to gain some quality.

  \Q

  How to do the trick? Well, CRF values of <math|\<pm\>6> \Pwill result in
  about half or twice the original bitrate\Q.
  (http://slhck.info/video/2017/03/01/rate-control.html), other things equal.
  If we know the bitrate of the source video, and it uses non-constrained
  CRF, we can derive the proper CRF.

  <\big-table>
    <block*|<tformat|<table|<row|<cell|B>|<cell|bitrate>>|<row|<cell|C>|<cell|CRF>>|<row|<cell|lossless>|<cell|uncompressed
    video stream <around*|(|YUV|)> decoded from
    source>>|<row|<cell|master>|<cell|given source video with known
    CRF>>|<row|<cell|target>|<cell|target video transcoded from master>>>>>
  </big-table|Definition of terms>

  <\eqnarray*>
    <tformat|<table|<row|<cell|B<rsub|lossless>/2<rsup|C<rsub|master>/6>>|<cell|=>|<cell|B<rsub|master>>>|<row|<cell|B<rsub|lossless>/2<rsup|C<rsub|target>/6>>|<cell|=>|<cell|B<rsub|target>>>|<row|<cell|<dfrac|1/2<rsup|C<rsub|master>/6>|1/2<rsup|C<rsub|target>/6>>>|<cell|=>|<cell|<dfrac|B<rsub|master>|B<rsub|target>>>>|<row|<cell|<dfrac|2<rsup|C<rsub|target>/6>|2<rsup|C<rsub|master>/6>>>|<cell|=>|<cell|<dfrac|B<rsub|master>|B<rsub|target>>>>|<row|<cell|ln<around*|(|2<rsup|C<rsub|target>/6>|)>-ln<around*|(|2<rsup|C<rsub|master>/6>|)>>|<cell|=>|<cell|ln<around*|(|B<rsub|master>|)>-ln<around*|(|B<rsub|target>|)>>>|<row|<cell|<around*|(|C<rsub|target>/6|)>ln<around*|(|2|)>-<around*|(|C<rsub|master>/6|)>ln<around*|(|2|)>>|<cell|=>|<cell|ln<around*|(|B<rsub|master>|)>-ln<around*|(|B<rsub|target>|)>>>|<row|<cell|<dfrac|ln<around*|(|2|)><around*|(|C<rsub|target>-C<rsub|master>|)>|6>>|<cell|=>|<cell|ln<around*|(|B<rsub|master>|)>-ln<around*|(|B<rsub|target>|)>>>|<row|<cell|C<rsub|target>>|<cell|=>|<cell|6\<cdot\><dfrac|ln<around*|(|B<rsub|master>|)>-ln<around*|(|B<rsub|target>|)>|ln<around*|(|2|)>>+C<rsub|master>>>>>
  </eqnarray*>

  \;
</body>

<\initial>
  <\collection>
    <associate|font|roman>
    <associate|font-base-size|12>
    <associate|math-font|roman>
    <associate|page-bot|15mm>
    <associate|page-even|15mm>
    <associate|page-odd|10mm>
    <associate|page-right|10mm>
    <associate|page-screen-margin|false>
    <associate|page-top|10mm>
    <associate|page-type|letter>
    <associate|par-columns|1>
    <associate|par-first|0fn>
    <associate|par-line-sep|0.030fns>
    <associate|par-mode|left>
    <associate|preamble|false>
  </collection>
</initial>

<\references>
  <\collection>
    <associate|auto-1|<tuple|1|?>>
  </collection>
</references>

<\auxiliary>
  <\collection>
    <\associate|table>
      <tuple|normal|Definition of terms|<pageref|auto-1>>
    </associate>
  </collection>
</auxiliary>