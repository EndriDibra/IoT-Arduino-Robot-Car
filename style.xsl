<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:template match="/">
    <html>
      <head>
        <style>
          table {
            border-collapse: collapse;
            width: 100%;
          }
          th, td {
            border: 1px solid black;
            padding: 8px;
            text-align: center;
          }
          th {
            background-color: #f2f2f2;
          }
        </style>
      </head>
      <body>
        <h1>Received Data</h1>
        <table>
          <thead>
            <tr>
              <th>Temperature</th>
              <th>Humidity</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><xsl:value-of select="data/item/Temperature"/></td>
              <td><xsl:value-of select="data/item/Humidity"/></td>
            </tr>
          </tbody>
        </table>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
