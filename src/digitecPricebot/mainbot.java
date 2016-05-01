package digitecPricebot;

import java.io.BufferedReader;
import java.io.InputStreamReader;

import org.apache.http.HttpEntity;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;
import java.io.*;

import java.text.Format;
import java.text.SimpleDateFormat;
import java.util.Calendar;

// used libs
// httpclient for (advanced) connecting to website, API: https://hc.apache.org/httpcomponents-client-ga/tutorial/html/
// jsoup for parsing html, API: http://jsoup.org/cookbook/introduction/parsing-a-document

public class mainbot {
	
	public static String digitec_urls = "digitec_urls.txt";
	public static String output_subfolder = "OUTPUT/";
	public static String input_subfolder = "INPUT/";
	
	public static void main(String[] args) {
		
		File urls = new File(input_subfolder + digitec_urls);
		// check if input file exists and is not a folder
		if(!urls.exists() || urls.isDirectory()) { 
		    System.err.println("could not find digitec_urls.txt");
		    System.err.println("aborting pricebot");
		} else {
			System.out.println("found input file digitec_urls.txt");
			
			// count the products in the input file
			int urlcount = 0;
			try{
				BufferedReader reader = new BufferedReader(new FileReader(input_subfolder + digitec_urls));
				while (reader.readLine() != null) urlcount++;
				reader.close();
			} catch (Exception rd) {
				rd.printStackTrace();
			}
			System.out.println(digitec_urls + " contains " + urlcount + " products");
			
			try{
				BufferedReader reader = new BufferedReader(new FileReader(input_subfolder + digitec_urls));
				
				for(int i=0; i<urlcount; i++){
					
					String urlnow = reader.readLine();
					System.out.println("opening : " + urlnow);
					// connect to website with apache httpclient
					CloseableHttpClient httpclient = HttpClients.createDefault();
					HttpGet httpget = new HttpGet(urlnow);
					
					try {
						try (CloseableHttpResponse chr = httpclient.execute(httpget)) {
							HttpEntity entity = chr.getEntity();
							if (entity != null) {
								// write html to string
								StringBuilder html = new StringBuilder();
								try (BufferedReader br = new BufferedReader(new InputStreamReader(entity.getContent()))) {
									String line;
									while ((line = br.readLine()) != null){
										html.append(line).append("\n");
									}
								}
								// parse html with jsoup
								Document doc = Jsoup.parse(html.toString());
								Elements brn = doc.getElementsByClass("product-brand");					// Element for brand
								Elements nam = doc.getElementsByAttributeValue("itemprop", "name");		// Element for product name
								Elements prc = doc.getElementsByAttributeValue("itemprop", "price");	// Element for priice
								
								// check if Elements could be found
								if(brn.size() == 0 || nam.size() == 0 || prc.size() == 0){
									if (brn.size() == 0){		// brand
										System.err.println("unable to retrieve brand");
										// System.err.println("aborting pricebot");
										// return;
									}
									if (nam.size() == 0){		// name
										System.err.println("unable to retrieve product name");
										// System.err.println("aborting pricebot");
										// return;
									}
									if (prc.size() == 0){		// price
										System.err.println("unable to retrieve price");
										// System.err.println("aborting pricebot");
										// return;
									}
								} else {
								
		
									// parse Elements to String
									Element brand = brn.first();
									for (Element element : brand.children()) {
										element.remove(); // also removes that object in pricediv (in parentobject)
									}
									String productbrand = brand.text().trim();
				
									Element name = nam.first();
	
									for (Element element : name.children()) {
										element.remove(); // also removes that object in pricediv (in parentobject)
									}
									String productname = name.text().trim();
									
									Element pricediv = prc.first();
	
									for (Element element : pricediv.children()) {
										element.remove(); // also removes that object in pricediv (in parentobject)
									}
									String productprice = pricediv.attr("content");
									
									System.out.println("successfully retrieved the following information :");
									System.out.println(productbrand);
									System.out.println(productname);
									System.out.println(productprice);
									
									// writing to output file
									appendPrice(productbrand, productname, productprice);
									// flush console
									try{Thread.sleep(100);}catch(InterruptedException ex){Thread.currentThread().interrupt();}
									System.out.println("#########################################");
								}
							}
						}
					} catch (Exception ex) {
						ex.printStackTrace();
					}
				}		// end of for loop
				reader.close();
				System.out.println("finnished task, exiting digitec price bot");
			} catch (Exception rd) {
				rd.printStackTrace();
			}
		}				// end file exists
	}					// end of main
	
	public static boolean appendPrice(String brand, String product, String price){
		// check arguments
		if(brand == null || product == null || price == null) return false;
		// generate the filename from the parameters
		String filename = "";
		// first, brand name followed by underscores to assemmble exactly 10 chars
		if(brand.length() < 10){
			filename += brand;
			while(filename.length() < 10){
				filename += "-";
			}
		} else {
			filename += brand.substring(0, 9);
		}
		filename += "_";
		// same with the product name, but with exactyl 40 chars (10 + 40 = 50)
		if(product.length() < 40){
			filename += product;
			while(filename.length() < 50){
				filename += "-";
			}
		} else {
			filename += product.substring(0, 39);
		}
		
		filename += ".txt";		// add file extension
		
		// check for output folder | create if inexistent
		File dir = new File(output_subfolder);
		if(!dir.exists() || !dir.isDirectory()){
			try{
		        dir.mkdir();
		    } 
		    catch(SecurityException se){
		        se.printStackTrace();
		    }        
		}
		
		filename = filename.replaceAll("[<>?/\":*|]", "");	// remove special (unallowed) characters like " or /
		filename = output_subfolder + filename;				// inside output folder
		
		File outjob = new File(filename);
		if(outjob.exists() && !outjob.isDirectory()) { 
		    System.out.println("writing to file : " + outjob.getAbsolutePath());
		    try {
		    	// get todays date
			    Format formatter = new SimpleDateFormat("yyyy.MM.dd");
			    java.util.Date today = Calendar.getInstance().getTime();
			    String reportDate = formatter.format(today);
			    
			    // check if today was already updated
			    String sLastLine = "", sCurrentLine = "";
			    BufferedReader reader = new BufferedReader(new FileReader(filename));
			    while ((sCurrentLine = reader.readLine()) != null) sLastLine = sCurrentLine;
			    reader.close();
			    sLastLine = sLastLine.substring(0, 10);
			    if(sLastLine.compareTo(reportDate) == 0){
			    	System.err.println("this file was already updated today, no changes applied");
			    	System.err.println("reported date was : \t" + reportDate);
			    } else {
			    // write date and price to the file
				    BufferedWriter writer = new BufferedWriter(new FileWriter(filename, true));
				    writer.newLine();
				    writer.write(reportDate + "\t" + price);
				    writer.close();
			    }
		    } catch (Exception e) {
		    	e.printStackTrace();
		    }
		} else {		// list does not yet exist
		    try {
		    	BufferedWriter writer = new BufferedWriter(new FileWriter(filename, true));
			    
		    	writer.write("brand        : " + brand +"\n");
			    writer.write("product name : " + product + "\n");
			    writer.write("########################################\n");
			    
			    Format formatter = new SimpleDateFormat("yyyy.MM.dd");
			    java.util.Date today = Calendar.getInstance().getTime();
			    String reportDate = formatter.format(today);
			    
			    // note, you don't have to check if it was already updated today
			    // the file has just been created
			    writer.write(reportDate + "\t" + price);
			    writer.close();
		    } catch (Exception e) {
		    	e.printStackTrace();
		    }
		    System.out.println("created file    : " + outjob.getAbsolutePath());
		}
		return true;
	}
}
