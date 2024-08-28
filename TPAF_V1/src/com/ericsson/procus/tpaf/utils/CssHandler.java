package com.ericsson.procus.tpaf.utils;

import java.io.File;

public class CssHandler {

	private String CssFileName;

	public CssHandler(){
		File css = new File(TPAFenvironment.CSSDIR+"\\" + TPAFenvironment.CSSFILENAME);
		if(css.exists()){
			CssFileName = "file:///"+css.getAbsolutePath();
		}else{
			CssFileName =  TPAFenvironment.CSSFILENAME;
		}
	}
	
	public String getCssFileName(){
		return CssFileName;
	}

	public void setCssFileName(String CssFileName){
		this.CssFileName = "file:./css/" + CssFileName;
	}
	
}
