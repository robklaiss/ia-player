const { parse } = require('querystring');
const { writeFile } = require('fs/promises');
const { v4: uuidv4 } = require('uuid');

const ALLOWED_TYPES = ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/x-matroska'];

module.exports.handler = async (event) => {
  try {
    const boundary = event.headers['content-type'].split('boundary=')[1];
    const bodyBuffer = Buffer.from(event.body, 'base64');
    
    // Parse multipart form data
    const parts = bodyBuffer.toString().split(`--${boundary}`);
    const filePart = parts.find(part => part.includes('filename='));
    
    if (!filePart) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: 'No file uploaded' })
      };
    }

    const [headers, ...content] = filePart.split('\r\n\r\n');
    const filenameMatch = headers.match(/filename="(.*?)"/);
    
    if (!filenameMatch) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: 'Invalid file upload' })
      };
    }

    const contentTypeMatch = headers.match(/Content-Type: (.*?)\r\n/);
    const contentType = contentTypeMatch ? contentTypeMatch[1] : 'application/octet-stream';

    if (!ALLOWED_TYPES.includes(contentType)) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: `Unsupported file type: ${contentType}` })
      };
    }

    const fileData = content.join('\r\n\r\n').trim();
    const uniqueName = `${uuidv4()}_${filenameMatch[1]}`;
    
    await writeFile(`public/uploads/${uniqueName}`, fileData, 'binary');

    return {
      statusCode: 200,
      body: JSON.stringify({
        filename: uniqueName,
        url: `/uploads/${uniqueName}`
      })
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: `Upload failed: ${error.message}` })
    };
  }
};
