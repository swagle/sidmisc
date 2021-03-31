function aptTime() {
  /**
  * This function will work for any locale. We convert to UTC and then to local time.
  * Make sure to keep offsets updated else we default to Pacific time.
  */
  
  var phoneNums = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('PhoneNumbers');
  var now = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('NOW');

  var prim = now.getSheetValues(12, 2, 1, 1);
  var sec = now.getSheetValues(12, 3, 1, 1);
  var primName = now.getSheetValues(8, 2, 1, 1);
  var secName = now.getSheetValues(8, 3, 1, 1);

  //Logger.log('primary = ' + prim + ', secondary = ' + sec);
  Logger.log('primary = ' + primName + ', secondary = ' + secName);
  
  // Please update the offsets here for new timezones added
  var offsets = {'PT': -8, 'IST': 5.5, 'CET': 1, 'ET': -5, 'HKT':8, 'Taiwan': 8};
  var dst_offsets = {'PT': -7, 'IST': 5.5, 'CET': 2, 'ET': -4, 'HKT':8, 'Taiwan': 8};

  if (!(prim in offsets)) prim = 'PT';

  Date.prototype.stdTimezoneOffset = function () {
    var jan = new Date(this.getFullYear(), 0, 1);
    var jul = new Date(this.getFullYear(), 6, 1);
    return Math.max(jan.getTimezoneOffset(), jul.getTimezoneOffset());
  }

  Date.prototype.isDstObserved = function () {
    return this.getTimezoneOffset() < this.stdTimezoneOffset();
  }

  // For todays date;
  Date.prototype.today = function () { 
    return ((this.getDate() < 10)?"0":"") + this.getDate() +"/"+(((this.getMonth()+1) < 10)?"0":"") + (this.getMonth()+1) +"/"+ this.getFullYear();
  }

  // For the time now
  Date.prototype.timeNow = function () {
     return ((this.getHours() < 10)?"0":"") + this.getHours() +":"+ ((this.getMinutes() < 10)?"0":"") + this.getMinutes() +":" 
     + ((this.getSeconds() < 10)?"0":"") +   this.getSeconds();
  }

  function getLocaleDate(tz) {
    var d = new Date();
    utc = d.getTime() + (d.getTimezoneOffset() * 60000);
    var offset = offsets[tz];
    if (d.isDstObserved()) offset = dst_offsets[tz];
    //Logger.log("isDstObserved = " + d.isDstObserved());
    return new Date(utc + (3600000 * offset));    
  }

  var primDate = getLocaleDate(prim);
  var secDate = getLocaleDate(sec);

  Logger.log("Primary:: localDate = " + primDate.today() + ", time = " + primDate.timeNow());
  Logger.log("Secondary:: localDate = " + secDate.today() + ", time = " + secDate.timeNow());
  
  // Check if local time not in between 11 pm and 7 am for primary
  // Else if it is between 11 am and 7 pm for secondary return primary
  var result = primName;
  if (primDate.getHours() > 22 || primDate.getHours() < 7) {
    if (secDate.getHours() > 22 || secDate.getHours() < 7) {
      result = primName;
    } else {
      result = secName;
    }
  }
  Logger.log('Result = ' + result);
  return result;  
}

