import QRCode from 'qrcode'
import { decryptPaste } from './crypto.coffee'

pasteToFile = (title, contents) ->
  fileContents = """
    #{title}

    #{contents}
    """
  url = URL.createObjectURL(
    new Blob [fileContents], type: 'text/plain;charset=utf-8'
  )
  link = document.createElement 'a'
  link.href = url
  link.download = "#{title}.txt"
  link.click()
  URL.revokeObjectURL link

pasteLinkToQr = ->
  qrCanvas = document.getElementById('qrCanvas')
  console.log qrCanvas
  qrCanvas.classList.remove("d-none");
  QRCode.toCanvas qrCanvas, window.location.href

processEncryptedPaste = (title, text) ->
  { decryptedTitle, decryptedText } = decryptPaste title, text

  if decryptedTitle? and decryptedText?
    document.getElementById('pasteTitle').innerText = decryptedTitle
    document.getElementById('pasteContents').innerText = decryptedText

getPasteFromPage = ->
  title = document.getElementById('pasteTitle').innerText
  contents = document.getElementById('pasteContents').innerText
  { title, contents }

export { pasteToFile, pasteLinkToQr, processEncryptedPaste }
