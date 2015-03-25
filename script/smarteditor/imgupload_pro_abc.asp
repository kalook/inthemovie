<%@ LANGUAGE="VBSCRIPT" %>
<%
   Response.Expires = -10000
   Server.ScriptTimeOut = 7200

   Set theForm = Server.CreateObject("ABCUpload4.XForm")
   theForm.AbsolutePath = True '절대경로 사용가능
   theForm.Overwrite = True    '덮어쓰기 가능
   theForm.CodePage = 949      '한글파일 가능하게

   imagepath = trim(theForm.item("imagepath"))
   irid = trim(theForm.item("id"))

   Set theField = theForm("update_image")(1)

   If theField.FileExists Then
      DirectoryPath = server.mappath("/") & Replace(imagepath,"/","\")
      strFileName = theField.SafeFileName

      If theField.Length > 4 * 1024 * 1024 Then
         Page_Msg_Back "4M 이상 파일은 업로드하실 수 없습니다."
         Response.end
      End If

      strFileWholePath = GetUniqueName(strFileName, DirectoryPath)

      theField.Save strFileWholePath
   End If

   Set fs = server.CreateObject("Scripting.FileSystemObject")
   strFileName = fs.GetFileName(strFileWholePath)

   With response
      .write "<script language=javascript>" & vbNewLine
      .write "  parent.parent.insertIMG('" & irid & "','" & strFileName & "');" & vbNewLine
      .write "  parent.parent.oEditors.getById[""" & irid & """].exec(""SE_TOGGLE_IMAGEUPLOAD_LAYER"");" & vbNewLine
      .write "</script>" & vbNewLine
   End With

   '//////////////////////////////////////////////////////////////////////////////////
   '// 파일관련
   '////////////////////////////////// ///////////////////////////////////////////////

    Function GetUniqueName(byRef strFileName, DirectoryPath)
        Dim strName, strExt
        strName = Mid(strFileName, 1, InstrRev(strFileName, ".") - 1)
        strExt  = Mid(strFileName, InstrRev(strFileName, ".") + 1)

        Dim fso
        Set fso = Server.CreateObject("Scripting.FileSystemObject")

        Dim bExist : bExist = True
        '우선 같은이름의 파일이 존재한다고 가정
        Dim strFileWholePath : strFileWholePath = DirectoryPath & "\" & strName & "." & strExt
        '저장할 파일의 완전한 이름(완전한 물리적인 경로) 구성
        Dim countFileName : countFileName = 0
        '파일이 존재할 경우, 이름 뒤에 붙일 숫자를 세팅함.

        Do While bExist ' 우선 있다고 생각함.
            If (fso.FileExists(strFileWholePath)) Then ' 같은 이름의 파일이 있을 때
                countFileName = countFileName + 1 '파일명에 숫자를 붙인 새로운 파일 이름 생성
                strFileName = strName & "(" & countFileName & ")." & strExt
                strFileWholePath = DirectoryPath & "\" & strFileName
            Else
                bExist = False
            End If
        Loop
        GetUniqueName = strFileWholePath
    End Function

   Sub Page_Msg_Back(msg)
      with response
         .write "<script language='javascript'>" & vbNewLine
         .write "  alert('" & msg & "');" & vbNewLine
         .write "  history.back();" & vbNewLine
         .write "</script>" & vbNewLine
      End with
   End Sub
%>